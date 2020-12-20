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
from datetime import date
from decimal import Decimal
import logging

from django.db import transaction

from student.roles import CourseCcxCoachRole, CourseInstructorRole, CourseStaffRole  # noqa pylint: disable=import-error

from figures.compat import (CourseEnrollment,
                            GeneratedCertificate,
                            StudentModule)
from figures.helpers import as_course_key, as_date, as_datetime, next_day, prev_day
import figures.metrics
from figures.models import CourseDailyMetrics, PipelineError
from figures.pipeline.logger import log_error
import figures.pipeline.loaders
from figures.pipeline.enrollment_metrics import bulk_calculate_course_progress_data
from figures.sites import UnlinkedCourseError, get_site_for_course


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


def get_average_progress_deprecated(course_id, date_for, course_enrollments):
    """Collects and aggregates raw course grades data
    """
    progress = []
    for ce in course_enrollments:
        try:
            course_progress = figures.metrics.LearnerCourseGrades.course_progress(ce)
            figures.pipeline.loaders.save_learner_course_grades(
                site=get_site_for_course(course_id),
                date_for=date_for,
                course_enrollment=ce,
                course_progress_details=course_progress['course_progress_details'])
        # TODO: Use more specific database-related exception
        except Exception as e:  # pylint: disable=broad-except
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

    if progress:
        progress_percent = [rec['progress_percent'] for rec in progress]
        average_progress = float(sum(progress_percent)) / float(len(progress_percent))
        average_progress = float(Decimal(average_progress).quantize(Decimal('.00')))
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


def extract_data_for_cdm(course_id, date_for, **_kwargs):
    """Extracts data needed for the given course and day's CDM model

    This function extracts data from the platform that will be used in the
    CourseDailyMetrics record for the given course and date_for
    """

    # We can turn this series of calls into a parallel
    # set of calls defined in a ruleset instead of hardcoded here after
    # retrieving the core quersets

    course_enrollments = get_enrolled_in_exclude_admins(course_id, date_for)
    course_enrollments_count = course_enrollments.count()

    active_learner_ids_today = get_active_learner_ids_today(course_id, date_for)
    if active_learner_ids_today:
        active_learners_today_count = active_learner_ids_today.count()
    else:
        active_learners_today_count = 0

    # Average progress
    try:
        progress_data = bulk_calculate_course_progress_data(course_id=course_id,
                                                            date_for=date_for)
        average_progress = progress_data['average_progress']
    except Exception:  # pylint: disable=broad-except
        # Broad exception for starters. Refine as we see what gets caught
        # Make sure we set the average_progres to None so that upstream
        # does not think things are normal
        average_progress = None
        msg = ('FIGURES:FAIL bulk_calculate_course_progress_data'
               ' date_for={date_for}, course_id="{course_id}"')
        logger.exception(msg.format(date_for=date_for, course_id=course_id))

    average_days_to_complete = get_average_days_to_complete(course_id, date_for)
    num_learners_completed = get_num_learners_completed(course_id, date_for)

    # Now bundle the data in to a dict and return
    # The reason we do it this way is that we want all of the data assembled
    # before we construct our return object
    return dict(date_for=date_for,
                course_id=course_id,
                enrollment_count=course_enrollments_count,
                active_learners_today=active_learners_today_count,
                average_progress=average_progress,
                average_days_to_complete=average_days_to_complete,
                num_learners_completed=num_learners_completed)


class CourseDailyMetricsLoader(object):

    def __init__(self, course_id):
        self.course_id = course_id
        self.site = get_site_for_course(self.course_id)
        if not self.site:
            raise UnlinkedCourseError(
                'No site found for course "{}"'.format(course_id))

    @transaction.atomic
    def save_metrics(self, date_for, data):
        """
        convenience method to handle saving and validating in a transaction

        Raises django.core.exceptions.ValidationError if the record fails
        validation
        """

        cdm, created = CourseDailyMetrics.objects.update_or_create(
            course_id=self.course_id,
            site=self.site,
            date_for=date_for,
            defaults=dict(
                enrollment_count=data['enrollment_count'],
                active_learners_today=data['active_learners_today'],
                average_progress=str(data['average_progress']),
                average_days_to_complete=int(round(data['average_days_to_complete'])),
                num_learners_completed=data['num_learners_completed'],
            )
        )
        cdm.clean_fields()
        return (cdm, created,)

    def load(self, date_for=None, force_update=False, **_kwargs):
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
        # TODO: The date assignments need testing for timezones
        # We have an assumption we're runnining in UTC. Probably ned to work on
        # this
        if not date_for:
            date_for = prev_day(date.today())
        else:
            date_for = as_date(date_for)
        try:
            cdm = CourseDailyMetrics.objects.get(course_id=self.course_id,
                                                 date_for=date_for)
            # record found, only update if force update flag is True
            if not force_update:
                return (cdm, False,)
        except CourseDailyMetrics.DoesNotExist:
            # record not found, move on to creating
            pass

        data = extract_data_for_cdm(course_id=self.course_id, date_for=date_for)
        return self.save_metrics(date_for=date_for, data=data)
