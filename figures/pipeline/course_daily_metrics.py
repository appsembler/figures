"""ETL for Course daily metrics

This module performs the following:

* Extracts data from edx-platform Django models and Modulestore objects
* Transforms data (mostly collecting aggregaates at this point)
* Loads data in to the Figures CourseDailyMetrics model
"""


# These are needed for the extractors
import datetime
from django.utils.timezone import utc

from certificates.models import GeneratedCertificate
from courseware.models import StudentModule
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from student.models import CourseEnrollment
from student.roles import CourseCcxCoachRole, CourseInstructorRole, CourseStaffRole

from figures.helpers import as_course_key, as_datetime, next_day, prev_day
import figures.metrics
from figures.models import CourseDailyMetrics, PipelineError
from figures.pipeline.logger import log_error
import figures.pipeline.loaders
from figures.serializers import CourseIndexSerializer

# TODO: Move extractors to figures.pipeline.extract module

# The extractors work locally on the LMS
# Future: add a remote mode to pull data via REST API

#
# Extraction helper methods
#


def get_course_enrollments(course_id, date_for):
    """Convenience method to get a filterd queryset of CourseEnrollment objects

    """
    return CourseEnrollment.objects.filter(
        course_id=as_course_key(course_id),
        created__lt=as_datetime(next_day(date_for)),
    )


def get_num_enrolled_in_exclude_admins(course_id, date_for):
    """
    Copied over from CourseEnrollmentManager.num_enrolled_in_exclude_admins method
    and modified to filter on date LT

    """
    course_locator = course_id

    if getattr(course_id, 'ccx', None):
        course_locator = course_id.to_course_locator()

    staff = CourseStaffRole(course_locator).users_with_role()
    admins = CourseInstructorRole(course_locator).users_with_role()
    coaches = CourseCcxCoachRole(course_locator).users_with_role()

    return CourseEnrollment.objects.filter(
        course_id=course_id,
        is_active=1,
        created__lt=as_datetime(next_day(date_for)),
    ).exclude(user__in=staff).exclude(user__in=admins).exclude(user__in=coaches).count()


def get_active_learner_ids_today(course_id, date_for):
    """Get unique user ids for learners who are active today for the given
    course and date

    """
    return StudentModule.objects.filter(
        course_id=as_course_key(course_id),
        modified=as_datetime(date_for)).values_list('student__id', flat=True).distinct()


def get_average_progress(course_id, date_for, course_enrollments):
    """Collects and aggregates raw course grades data
    """
    progress = []

    for ce in course_enrollments:
        try:
            course_progress = figures.metrics.LearnerCourseGrades.course_progress(ce)
            figures.pipeline.loaders.save_learner_course_grades(
                date_for=date_for,
                course_enrollment=ce,
                course_progress_details=course_progress['course_progress_details'])
        except Exception as e:
            error_data = dict(
                msg='Unable to get course blocks',
                username=ce.user.username,
                course_id=str(ce.course_id),
                exception=str(e),
                )
            log_error(
                error_data=error_data,
                error_type=PipelineError.GRADES_DATA,
                user=ce.user,
                course_id=ce.course_id,
                )
            course_progress = dict(
                progress_percent=0.0,
                course_progress_details=None)
        if course_progress:
            progress.append(course_progress)
    if len(progress):
        progress_percent = [rec['progress_percent'] for rec in progress]
        average_progress = float(sum(progress_percent)) / float(len(progress_percent))
    else:
        average_progress = 0.0

    return average_progress


def get_days_to_complete(course_id, date_for):
    """Return a dict with a list of days to complete and errors

    NOTE: This is a work in progress, as it has issues to resolve:
    * It returns the delta in days, so working in ints
    * This means if a learner starts at midnight and finished just before
      midnight, then 0 days will be given

    NOTE: This has limited scaling. We ought to test it with
    1k, 10k, 100k cert records

    TODO: change to use start_date, end_date with defaults that
    start_date is open and end_date is today

    TODO: Consider collecting the total seconds rather than days
    This will improve accuracy, but may actually not be that important
    TODO: Analyze the error based on number of completions

    When we have to support scale, we can look into optimization
    techinques.
    """
    certificates = GeneratedCertificate.objects.filter(
        course_id=as_course_key(course_id),
        created_date__lte=as_datetime(date_for))

    days = []
    errors = []
    for cert in certificates:
        ce = CourseEnrollment.objects.filter(
            course_id=as_course_key(course_id),
            user=cert.user)
        # How do we want to handle multiples?
        if ce.count() > 1:
            errors.append(
                dict(msg='Multiple CE records',
                     course_id=course_id,
                     user_id=cert.user.id,
                     ))
        days.append((cert.created_date - ce[0].created).days)
    return dict(days=days, errors=errors)


def calc_average_days_to_complete(days):
    rec_count = len(days)
    if rec_count:
        return float(sum(days)) / float(rec_count)
    else:
        return 0.0


def get_average_days_to_complete(course_id, date_for):

    days_to_complete = get_days_to_complete(course_id, date_for)
    # TODO: Track any errors in getting days to complete
    # This is in days_to_complete['errors']
    average_days_to_complete = calc_average_days_to_complete(
        days_to_complete['days'])
    return average_days_to_complete


def get_num_learners_completed(course_id, date_for):
    certificates = GeneratedCertificate.objects.filter(
        course_id=as_course_key(course_id),
        created_date__lt=as_datetime(next_day(date_for)))
    return certificates.count()

# Formal extractor classes


class CourseIndicesExtractor(object):
    """
    Extract a list of course index dicts
    """

    def extract(self, **kwargs):
        """
        TODO: Add filters in the kwargs
        """

        filter_args = kwargs.get('filters', {})
        queryset = CourseOverview.objects.filter(**filter_args)
        return CourseIndexSerializer(queryset, many=True)


class CourseDailyMetricsExtractor(object):
    """
    Prototype extractor to get data needed for CourseDailyMetrics

    Next step is to break out the functionality from here to
    separate extractors so we have more reusability
    BUT, we will then need to find a transform
    """

    def extract(self, course_id, date_for=None, **kwargs):
        """
            defaults = dict(
                enrollment_count=data['enrollment_count'],
                active_learners_today=data['active_learners_today'],
                average_progress=data.get('average_progress', None),
                average_days_to_complete=data.get('average_days_to_complete, None'),
                num_learners_completed=data['num_learners_completed'],
            )
        """

        # Update args if not assigned
        if not date_for:
            date_for = prev_day(
                datetime.datetime.utcnow().replace(tzinfo=utc).date()
            )

        # We can turn this series of calls into a parallel
        # set of calls defined in a ruleset instead of hardcoded here
        # Get querysets and datasets we'll use
        # We do this to reduce calls

        course_enrollments = get_course_enrollments(
            course_id, date_for,)

        data = dict(date_for=date_for, course_id=course_id)

        # This is the transform step
        # After we get this working, we can then define them declaratively
        # we can do a lambda for course_enrollments to get the count

        data['enrollment_count'] = course_enrollments.count()
        active_learner_ids_today = get_active_learner_ids_today(
            course_id, date_for,)
        if active_learner_ids_today:
            active_learners_today = active_learner_ids_today.count()
        else:
            active_learners_today = 0

        data['active_learners_today'] = active_learners_today
        data['average_progress'] = get_average_progress(
            course_id, date_for, course_enrollments,)
        data['average_days_to_complete'] = get_average_days_to_complete(
            course_id, date_for,)
        data['num_learners_completed'] = get_num_learners_completed(
            course_id, date_for,)

        return data


class CourseDailyMetricsLoader(object):

    def __init__(self, course_id):
        self.course_id = course_id
        self.extractor = CourseDailyMetricsExtractor()

    def get_data(self, date_for):
        return self.extractor.extract(
            course_id=self.course_id,
            date_for=date_for)

    def load(self, date_for=None, force_update=False, **kwargs):
        """
        TODO: clean up how we do this. We want to be able to call the loader
        with an existing data set (not having to call the extractor) but we
        need to make sure that the metrics row 'date_for' is the same as
        provided in the data. So before hacking something together, I want to
        think this over some more.

        """
        if not date_for:
            date_for = prev_day(
                datetime.datetime.utcnow().replace(tzinfo=utc).date()
            )

        # if we already have a record for the date_for and force_update is False
        # then skip getting data
        if not force_update:
            try:
                cdm = CourseDailyMetrics.objects.get(
                    course_id=self.course_id,
                    date_for=date_for)
                return (cdm, False,)

            except CourseDailyMetrics.DoesNotExist:
                # proceed normally
                pass

        data = self.get_data(date_for=date_for)
        cdm, created = CourseDailyMetrics.objects.update_or_create(
            course_id=self.course_id,
            date_for=date_for,
            defaults=dict(
                enrollment_count=data['enrollment_count'],
                active_learners_today=data['active_learners_today'],
                average_progress=data['average_progress'],
                average_days_to_complete=data['average_days_to_complete'],
                num_learners_completed=data['num_learners_completed'],
            )
        )
        return (cdm, created,)
