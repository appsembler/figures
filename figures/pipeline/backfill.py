"""Backfills metrics models

Initially developed to support API performance improvements
"""

from __future__ import absolute_import
import os
from time import time
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.utils.timezone import utc

from figures.compat import CourseNotFound
from figures.course import Course
from figures.helpers import as_date
from figures.models import EnrollmentData
from figures.sites import (
    get_course_enrollments_for_site,
    get_course_keys_for_site,
    get_student_modules_for_site
)
from figures.pipeline.course_daily_metrics import CourseDailyMetricsLoader
from figures.pipeline.site_daily_metrics import SiteDailyMetricsLoader
from figures.pipeline.site_monthly_metrics import fill_month

# Backfill is done irregularly on an as-needed basis and not part of regularly
# scheduled operations.
# Default to a directory for which the edxapp user already has permissions
# This is an interim implementation is for expediency. We can then follow up
# with discussion on where a more ideal location would be. Perhaps in
# `/edx/var/log/figures`. However, the `/edx/var/log` directory does not have
# write permission for the `edxapp` or `www-data` users, while `/edx/app/edxapp`
# does. Therefore we initally declar the following to write backfill logs
DEFAULT_FIGURES_BACKFILL_LOG_DIR = '/edx/app/edxapp/figures/logs/'


class InvalidDataError(Exception):
    """Raised when wrong data are used, like cross-site data processing

    Initially created to raise an exception if cached data or data provided as
    function parameters do not belong to the site being processed.
    """
    pass


def figures_backfill_log_dir():
    """Specify where to write Figures backfill log files
    """
    return settings.ENV_TOKENS['FIGURES'].get('BACKFILL_LOG_DIR',
                                              DEFAULT_FIGURES_BACKFILL_LOG_DIR)


# This function called just by mgmt command, backfill_figures_monthly_metrics.py
def backfill_monthly_metrics_for_site(site, overwrite=False, use_raw_sql=False):
    """Backfill specified months' historical site metrics for the specified site
    """
    site_sm = get_student_modules_for_site(site)
    if not site_sm:
        return None

    first_created = site_sm.order_by('created').first().created

    start_month = datetime(year=first_created.year,
                           month=first_created.month,
                           day=1,
                           tzinfo=utc)
    last_month = datetime.utcnow().replace(tzinfo=utc) - relativedelta(months=1)
    backfilled = []
    for dt in rrule(freq=MONTHLY, dtstart=start_month, until=last_month):
        obj, created = fill_month(site=site,
                                  month_for=dt,
                                  student_modules=site_sm,
                                  overwrite=overwrite,
                                  use_raw=use_raw_sql)
        backfilled.append(dict(obj=obj, created=created, dt=dt))

    return backfilled


def backfill_enrollment_data_for_site(site):
    """Convenience function to fill EnrollmentData records

    This backfills EnrollmentData records for existing CourseEnrollment
    and LearnerCourseGradeMetrics records.

    The only exception it handles is `figures.compat.CourseNotFound`. All other
    exceptions are passed through this function to its caller.

    Potential improvements: iterate by course id within site, have a function
    specific to a course. more queries, but breaks up the work

    TODO: move the contents of this function to
      `figures.tasks.update_enrollment_data`

    TODO: Performance and handling improvement:
      * Get course ids for which the site has enrollments (Skip over courses
        without enrollments)
      * Check if the course actually exists
      * If so, iterate over enrollments for the course
      * Else log the error. This is a good candidate to track in a Figures
        model, like a future reworked 'PipelineError'
    """
    enrollment_data = []
    errors = []
    site_course_enrollments = get_course_enrollments_for_site(site)
    for rec in site_course_enrollments:
        try:
            obj, created = EnrollmentData.objects.set_enrollment_data(
                site=site,
                user=rec.user,
                course_id=rec.course_id)
            enrollment_data.append((obj, created))
        except CourseNotFound:
            msg = ('CourseNotFound for course "{course}". '
                   ' CourseEnrollment ID={ce_id}')
            errors.append(msg.format(course=str(rec.course_id),
                                     ce_id=rec.id))

    return dict(results=enrollment_data, errors=errors)


def get_courses_first_enrollment_timestamps(site, as_strings=False):
    """Return dict of course_id and first enrolled on date
    key is the course_id, value is the date of the first enrollment

    The dict returned by this function is used to determine which courses need
    to be backfilled for a given date.

    We have this as a seperate function so that the caller can generate the
    mapping once to process over a set of days

    The `as_strings` param is used to make it easier to serialize the data to
    file
    """
    data = dict()
    for course_key in get_course_keys_for_site(site):
        created = Course(course_key).first_enrollment_timestamp()
        if as_strings:
            data[str(course_key)] = created.isoformat()
        else:
            data[course_key] = created
    return data


def courses_enrolled_on_or_before(site, date_for, data=None):
    """list courses that have enrollments created on or befor the date
    if data is passed in, assumes the date values are `datetime.date`

    For the time being, this is a "getter" function instead of a generator so
    that we can fail before updating Figures course daily metrics records in
    the event that a set of data contain courses that do not belong to the site
    """
    check_course_ids = get_course_keys_for_site(site)
    if data is None:
        data = get_courses_first_enrollment_timestamps(site)
    date_for = as_date(date_for)
    course_ids = []
    for course_id, created in data.items():
        if course_id not in check_course_ids:
            msg = 'Aborting: "Course {course_id}" does not belong to site "{domain}"'
            raise InvalidDataError(msg.format(course_id=str(course_id),
                                              domain=site.domain))

        # if not created, then there are no enrollments in the course and we skip it
        if created and as_date(created) <= date_for:
            course_ids.append(course_id)
    return course_ids


def backfill_daily_metrics_for_site_and_date(site,
                                             date_for,
                                             process_sdm=True,
                                             logdir=None,
                                             force_update=False):
    """To be run by Django management command or in Django shell

    To note, this function was originally an ad-hoc script.

    This function creates `CourseDailyMetrics` records for each course for the
    specified site and day. It then creates the `SiteDailyMetrics` record for
    the site and day.

    Progress is tracked in a log file with the default directory in this
    module's `DEFAULT_FIGURES_BACKFILL_LOG_DIR` variable. This can be overriden
    in the settings "server-vars" file, like so:

    ```
    EDXAPP_ENV_EXTRA:
      FIGURES:
        BACKFILL_LOG_DIR: '/alternate/path/to/figures/backfill/logs'
    ```

    ## On progress

    Progress will only be updated if we run backfill for the previous calendar
    day. This is a bit of combined feature of Figures pipeline code and a
    limitation in that there's not a ready way to extract historical progress
    for a learner "on this date in the past".
    """
    date_for = as_date(date_for)
    date_for_str = date_for.isoformat()

    if logdir is None:
        logdir = figures_backfill_log_dir()

    filename = 'backfill-for-site-{site_id}-date-{date_for}.log'.format(
        site_id=site.id, date_for=date_for_str)
    filepath = os.path.join(logdir, filename)

    course_ids = courses_enrolled_on_or_before(site, date_for)
    course_id_count = len(course_ids)

    # The log file has the site id and date for as identifiers
    # We have the log file in append mode so that we don't overwrite the existing
    # file in case something fails, we can pick up the logging in the same file
    # when restarting the backfill for the same site and date
    # if we find doing the log file in append more some kind of pain point, we
    # can improve the engineering then
    with open(filepath, 'a', encoding='utf-8') as logfile:
        start_time = time()
        logfile.write('START: backfill {} courses, date_for: {}\n'.format(
            course_id_count, date_for_str))
        for i, course_id in enumerate(course_ids):
            logfile.write('[{} of {}] date_for: {}, {}\n'.format(
                i+1, course_id_count, date_for_str, str(course_id)))

            cdm_obj, _created = CourseDailyMetricsLoader(
                str(course_id)).load(date_for=date_for, force_update=force_update)
            logfile.write('-- wrote CDM id: {}\n'.format(cdm_obj.id))

            # We flush so we can tail the log file for progress
            logfile.flush()
        cdms_elapsed = time() - start_time
        logfile.write('\nEND: backfill courses. date_for:{}, elapsed: {}\n'.format(
            date_for_str, cdms_elapsed))
        if process_sdm:
            # TODO: if the SDM already exists, report it. This means the admin
            # can decide to manually force update, which is usually what we
            # want, however, we don't want surprise modifications of existing
            # data, so we're leaving it up to the caller to explicitly say
            # "destroy and rewrite"
            logfile.write('START: backfill site {} for date {}: \n'.format(
                site.domain, date_for_str))
            start_time = time()
            sdm_obj, _created = SiteDailyMetricsLoader().load(site=site,
                                                              date_for=date_for,
                                                              force_update=force_update)
            logfile.write('-- wrote SDM id: {}\n'.format(sdm_obj.id))
            sdm_elapsed = time() - start_time
            logfile.write('\nEND: backfill site. date_for: {}, elapsed: {}\n'.format(
                date_for_str, sdm_elapsed))

    # return location of logfile and some instrumentation data
    return dict(
        logfile=filepath,
        courses_processed=course_id_count,
        cdms_elapsed=cdms_elapsed,
        sdm_elapsed=sdm_elapsed)
