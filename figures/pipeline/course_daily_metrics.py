"""ETL for Course Daily Metrics (CDM)

This module performs the following:

* Extracts data from edx-platform Django models and Modulestore objects
* Transforms data (mostly collecting aggregaates at this point)
* Loads data in to the Figures CourseDailyMetrics model

The extractors work locally on the LMS
Future: add a remote mode to pull data via REST API

# TODO: Move extractors to figures.pipeline.extract module
"""
from __future__ import absolute_import
import logging

from dateutil.relativedelta import relativedelta
from django.db import transaction

from student.roles import CourseCcxCoachRole, CourseInstructorRole, CourseStaffRole  # noqa pylint: disable=import-error

from figures.compat import (CourseEnrollment,
                            CourseOverview,
                            GeneratedCertificate,
                            StudentModule)
from figures.helpers import as_course_key, as_datetime, is_past_date, next_day
import figures.metrics
from figures.models import CourseDailyMetrics
from figures.pipeline.enrollment_metrics import bulk_calculate_course_progress_data
from figures.pipeline.enrollment_metrics_next import (
    calculate_course_progress as calculate_course_progress_next
)

from figures.serializers import CourseIndexSerializer
import figures.sites
from figures.pipeline.helpers import pipeline_date_for_rule


logger = logging.getLogger(__name__)


# Extraction helper methods


def get_enrolled_in_exclude_admins(course_id, date_for=None):
    """
    Copied over from CourseEnrollmentManager.num_enrolled_in_exclude_admins method
    and modified to filter on date LT

    If no date is provided then the date is not used as a filter

    """
    course_locator = as_course_key(course_id)

    if getattr(course_id, 'ccx', None):
        course_locator = course_id.to_course_locator()

    staff = CourseStaffRole(course_locator).users_with_role()
    admins = CourseInstructorRole(course_locator).users_with_role()
    coaches = CourseCcxCoachRole(course_locator).users_with_role()
    filter_args = dict(course_id=course_locator, is_active=1)

    if date_for:
        filter_args.update(dict(created__lt=as_datetime(next_day(date_for))))

    return CourseEnrollment.objects.filter(**filter_args).exclude(
        user__in=staff).exclude(user__in=admins).exclude(user__in=coaches)


def get_active_learner_ids_today(course_id, date_for):
    """Get unique user ids for learners who are active today for the given
    course and date

    Note: When Figures no longer has to support Django 1.8, we can simplify
    this date check:
        https://docs.djangoproject.com/en/1.9/ref/models/querysets/#date
    """
    date_for_as_datetime = as_datetime(date_for)
    return StudentModule.objects.filter(
        course_id=as_course_key(course_id),
        modified__year=date_for_as_datetime.year,
        modified__month=date_for_as_datetime.month,
        modified__day=date_for_as_datetime.day,
        ).values_list('student__id', flat=True).distinct()


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
        try:
            days.append((cert.created_date - ce[0].created).days)
        except IndexError:
            # sometimes a course enrollment is deleted after the cert is generated.  why, who knows?
            # in which case just leave out that data
            errors.append(
                dict(msg='No CourseEnrollment matching user course certificate',
                     course_id=course_id,
                     user_id=cert.user.id,
                     ))
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
    """
    Get the total number of certificates generated for the course up to the
    'date_for' date

    We will need to relabel this to "certificates"

    We may want to get the number of certificates granted in the given day
    """
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

    def extract(self, course_id, date_for, ed_next=False, **_kwargs):
        """Extracts (collects) aggregated course level data

        Args:
            course_id (:obj:`str` or :obj:`CourseKey`): The course for which we collect data
            date_for (str or date): Deprecated. Was to backfill data.
                Specialized TBD backfill data will be called instead.
            ed_next (bool, optional): "Enrollment Data Next" flag. If set to `True`
                then we collect metrics with our updated workflow. See here:
                https://github.com/appsembler/figures/issues/428

        Returns:
            dict with aggregate course level metrics

            ```
            dict(
                enrollment_count=data['enrollment_count'],
                active_learners_today=data['active_learners_today'],
                average_progress=data.get('average_progress', None),
                average_days_to_complete=data.get('average_days_to_complete, None'),
                num_learners_completed=data['num_learners_completed'],
            )
            ```

        TODO: refactor this class. It doesn't need to be a class. Can be a
        standalone function
        Add lazy loading method to load course enrollments
        - Create a method for each metric field
        """

        # We can turn this series of calls into a parallel
        # set of calls defined in a ruleset instead of hardcoded here after
        # retrieving the core quersets

        course_enrollments = get_enrolled_in_exclude_admins(
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

        # Average progress
        # Progress data cannot be reliable for backfills or for any date prior to yesterday
        # without using StudentModuleHistory so we skip getting this data if running
        # for a day earlier than previous day (i.e., not during daily update of CDMs),
        #  especially since it is so expensive to calculate.
        # Note that Avg() applied across null and decimal vals for aggregate average_progress
        # will correctly ignore nulls
        # TODO: Reconsider this if we implement either StudentModuleHistory-based queries
        # (if so, you will need to add any types you want to
        # StudentModuleHistory.HISTORY_SAVING_TYPES)
        # TODO: Reconsider this once we switch to using Persistent Grades
        if is_past_date(date_for + relativedelta(days=1)):  # more than 1 day in past
            data['average_progress'] = None
            msg = ('FIGURES:PIPELINE:CDM Declining to calculate average progress for a past date'
                   ' date_for={date_for}, course_id="{course_id}"')
            logger.debug(msg.format(date_for=date_for, course_id=course_id))
        else:
            try:
                # This conditional check is an interim solution until we make
                # the progress function configurable and able to run Figures
                # plugins
                if ed_next:
                    progress_data = calculate_course_progress_next(course_id=course_id)
                else:
                    progress_data = bulk_calculate_course_progress_data(course_id=course_id,
                                                                        date_for=date_for)
                data['average_progress'] = progress_data['average_progress']
            except Exception:  # pylint: disable=broad-except
                # Broad exception for starters. Refine as we see what gets caught
                # Make sure we set the average_progres to None so that upstream
                # does not think things are normal
                data['average_progress'] = None

                if ed_next:
                    prog_func = 'calculate_course_progress_next'
                else:
                    prog_func = 'bulk_calculate_course_progress_data'

                msg = ('FIGURES:FAIL {prog_func}'
                       ' date_for={date_for}, course_id="{course_id}"')
                logger.exception(msg.format(prog_func=prog_func,
                                            date_for=date_for,
                                            course_id=course_id))

        data['average_days_to_complete'] = get_average_days_to_complete(
            course_id, date_for,)

        data['num_learners_completed'] = get_num_learners_completed(
            course_id, date_for,)

        return data


class CourseDailyMetricsLoader(object):

    def __init__(self, course_id):
        self.course_id = course_id
        # TODO: Consider adding extractor as optional param
        self.extractor = CourseDailyMetricsExtractor()
        self.site = figures.sites.get_site_for_course(self.course_id)

    def get_data(self, date_for, ed_next=False):
        return self.extractor.extract(
            course_id=self.course_id,
            date_for=date_for,
            ed_next=ed_next)

    @transaction.atomic
    def save_metrics(self, date_for, data):
        """
        convenience method to handle saving and validating in a transaction

        Raises django.core.exceptions.ValidationError if the record fails
        validation
        """
        defaults = dict(
            enrollment_count=data['enrollment_count'],
            active_learners_today=data['active_learners_today'],
            average_days_to_complete=int(round(data['average_days_to_complete'])),
            num_learners_completed=data['num_learners_completed'],
        )
        if data['average_progress'] is not None:
            defaults['average_progress'] = str(data['average_progress'])

        cdm, created = CourseDailyMetrics.objects.update_or_create(
            course_id=str(self.course_id),
            site=self.site,
            date_for=date_for,
            defaults=defaults
        )
        cdm.clean_fields()
        return (cdm, created,)

    def load(self, date_for=None, ed_next=False, force_update=False, **_kwargs):
        """
        TODO: clean up how we do this. We want to be able to call the loader
        with an existing data set (not having to call the extractor) but we
        need to make sure that the metrics row 'date_for' is the same as
        provided in the data. So before hacking something together, I want to
        think this over some more.

        If the record alrdady exists and force_update is False, then simply
        return the record with the 'created' flag to False. This saves us an
        unnecessary call to extract data

        Raises ValidationError if invalid data is attempted to be saved to the
        course daily metrics model instance
        """
        date_for = pipeline_date_for_rule(date_for)
        try:
            cdm = CourseDailyMetrics.objects.get(course_id=str(self.course_id),
                                                 date_for=date_for)
            # record found, only update if force update flag is True
            if not force_update:
                return (cdm, False,)
        except CourseDailyMetrics.DoesNotExist:
            # record not found, move on to creating
            pass

        data = self.get_data(date_for=date_for, ed_next=ed_next)
        return self.save_metrics(date_for=date_for, data=data)
