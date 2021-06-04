"""
Figures Celery tasks. Initially this module contains tasks for the ETL pipeline.

The higher level task is responsible for error handling of functions it calls

"""
from __future__ import absolute_import
import datetime
import time

import six
import waffle

from django.contrib.sites.models import Site
from django.utils.timezone import utc

from celery import chord, group
from celery.app import shared_task
from celery.utils.log import get_task_logger

from figures.backfill import backfill_enrollment_data_for_site
from figures.compat import CourseEnrollment, CourseOverview
from figures.helpers import as_course_key, as_date
from figures.log import log_exec_time
from figures.pipeline.course_daily_metrics import CourseDailyMetricsLoader
from figures.pipeline.site_daily_metrics import SiteDailyMetricsLoader
from figures.sites import get_sites, site_course_ids
from figures.pipeline.mau_pipeline import collect_course_mau
from figures.pipeline.helpers import DateForCannotBeFutureError
from figures.pipeline.site_monthly_metrics import fill_last_month as fill_last_smm_month


logger = get_task_logger(__name__)

# Consistent log message prefixes for easier log grepping
FPD_LOG_PREFIX = 'FIGURES:PIPELINE:DAILY'
FPM_LOG_PREFIX = 'FIGURES:PIPELINE:MONTHLY'

# For debugging in the devstack celery worker, unremark this line
# This can reduce the noise over seting the log level to info via the Celery
# worker command line, ``./manage.py celery worker -l INFO --settings=devstack``
#
# TODO: Make this configurable in the settings
# logger.setLevel('INFO')

WAFFLE_DISABLE_PIPELINE = 'figures.disable_pipeline'


@shared_task
def populate_single_cdm(course_id, date_for=None, force_update=False):
    """Populates a CourseDailyMetrics record for the given date and course

    The calling function is responsible for error handling calls to this
    function
    """
    if date_for:
        date_for = as_date(date_for)

    # Provide info in celery log
    learner_count = CourseEnrollment.objects.filter(
        course_id=as_course_key(course_id)).count()
    msg = 'populate_single_cdm. course id = "{}", learner count={}'.format(
        course_id, learner_count)
    logger.debug(msg)

    start_time = time.time()

    cdm_obj, _created = CourseDailyMetricsLoader(
        course_id).load(date_for=date_for, force_update=force_update)
    elapsed_time = time.time() - start_time
    logger.debug('done. Elapsed time (seconds)={}. cdm_obj={}'.format(
        elapsed_time, cdm_obj))


@shared_task
def populate_single_sdm(site_id, date_for, force_update=False):
    """Populate a SiteDailyMetrics record

    This is simply a Celery task wrapper around the call to collect data into
    the SiteDailyMetrics record for the given site and date_for.
    """
    logger.debug('populate_single_sdm: site_id={}'.format(site_id))

    SiteDailyMetricsLoader().load(site=Site.objects.get(id=site_id),
                                  date_for=date_for,
                                  force_update=force_update)

    logger.debug(
        'done running populate_site_daily_metrics for site_id={}'.format(site_id))


@shared_task
def populate_daily_metrics_for_site(site_id, date_for, force_update=False):
    """Collect metrics for the given site and date
    """
    try:
        site = Site.objects.get(id=site_id)
    except Site.DoesNotExist as e:
        msg = ('{prefix}:SITE:FAIL:populate_daily_metrics_for_site:site_id: '
               '{site_id} does not exist')
        logger.exception(msg.format(prefix=FPD_LOG_PREFIX, site_id=site_id))
        raise e

    for course_id in site_course_ids(site):
        try:
            populate_single_cdm(course_id=course_id,
                                date_for=date_for,
                                force_update=force_update)
        except Exception as e:  # pylint: disable=broad-except
            msg = ('{prefix}:SITE:COURSE:FAIL:populate_daily_metrics_for_site.'
                   ' site_id:{site_id}, date_for:{date_for}. course_id:{course_id}'
                   ' exception:{exception}')
            logger.exception(msg.format(prefix=FPD_LOG_PREFIX,
                                        site_id=site_id,
                                        date_for=date_for,
                                        course_id=str(course_id),
                                        exception=e))
    populate_single_sdm(site_id=site.id,
                        date_for=date_for,
                        force_update=force_update)


@shared_task
def update_enrollment_data(site_id, **_kwargs):
    """
    This can be an expensive task as it iterates over all the enrollments in a
    site

    We can reduce the records for which we need to iterate if we filter on
    CourseEnrollment.objects.filter(is_actie=True)

    However, we have to ensure that we don't exclude learners who have just
    completed a course and are awaiting post course activities, like being
    awarded a certificate
    """
    try:
        site = Site.objects.get(id=site_id)
        results = backfill_enrollment_data_for_site(site)
        if results.get('errors'):
            for rec in results['errors']:
                logger.error('figures.tasks.update_enrollment_data. Error:{}'.format(rec))
    except Site.DoesNotExist:
        logger.error(
            'figurs.tasks.update_enrollment_data: site_id={} does not exist'.format(
                site_id))
    except Exception:  # pylint: disable=broad-except
        msg = ('FIGURES:DAILYLFAIL daily metrics:update_enrollment_data'
               ' for site_id={}'.format(site_id))
        logger.exception(msg)


# TODO: Sites iterator with entry and exit logging


@shared_task
def populate_daily_metrics(date_for=None, force_update=False):
    """Runs Figures daily metrics collection

    This is a top level Celery task run every 24 hours to collect metrics.

    It iterates over each site to populate CourseDailyMetrics records for the
    courses in each site, then populates that site's SiteDailyMetrics record.

    Developer note: Errors need to be handled at each layer in the call chain
    1. Site
    2. Course
    3. Learner
    and for any auxiliary data collection that may be added in the future to
    this task. Those need to be wrapped in `try/ecxcept` blocks too

    This function will get reworked so that each site runs in its own
    """
    if waffle.switch_is_active(WAFFLE_DISABLE_PIPELINE):
        logger.warning('Figures pipeline is disabled due to %s being active.',
                       WAFFLE_DISABLE_PIPELINE)
        return

    # The date_for handling is very similar to the new rule we ahve in
    # `figures.pipeline.helpers.pipeline_data_for_rule`
    # The difference is the following code does not set 'date_for' as yesterday
    # So we likely want to rework the pipeline rule function and this code
    # so that we have a generalized date_for rule that can take an optional
    # transform function, like `prev_day`

    today = datetime.datetime.utcnow().replace(tzinfo=utc).date()
    # TODO: Decide if/how we want any special logging if we get an exception
    # on 'casting' the date_for argument as a datetime.date object
    if date_for:
        date_for = as_date(date_for)
        if date_for > today:
            msg = '{prefix}:ERROR - Attempted pipeline call with future date: "{date_for}"'
            raise DateForCannotBeFutureError(msg.format(prefix=FPD_LOG_PREFIX,
                                                        date_for=date_for))
        # Don't update enrollment data if we are backfilling (loading data for
        # previous dates) as it is expensive
    else:
        date_for = today

    do_update_enrollment_data = False if date_for < today else True
    sites = get_sites()
    sites_count = sites.count()

    # This is our task entry log message
    msg = '{prefix}:START:date_for={date_for}, site_count={site_count}'
    logger.info(msg.format(prefix=FPD_LOG_PREFIX,
                           date_for=date_for,
                           site_count=sites_count))

    for i, site in enumerate(sites):

        msg = '{prefix}:SITE:START:{id}:{domain} - Site {i:04d} of {n:04d}'
        logger.info(msg.format(prefix=FPD_LOG_PREFIX,
                               id=site.id,
                               domain=site.domain,
                               i=i,
                               n=sites_count))
        try:
            populate_daily_metrics_for_site(site_id=site.id,
                                            date_for=date_for,
                                            force_update=force_update)

        except Exception:  # pylint: disable=broad-except
            msg = ('{prefix}:FAIL populate_daily_metrics unhandled site level'
                   ' exception for site[{site_id}]={domain}')
            logger.exception(msg.format(prefix=FPD_LOG_PREFIX,
                                        site_id=site.id,
                                        domain=site.domain))

        # Until we implement signal triggers
        if do_update_enrollment_data:
            try:
                update_enrollment_data(site_id=site.id)
            except Exception:  # pylint: disable=broad-except
                msg = ('{prefix}:FAIL figures.tasks update_enrollment_data '
                       ' unhandled exception. site[{site_id}]:{domain}')
                logger.exception(msg.format(prefix=FPD_LOG_PREFIX,
                                            site_id=site.id,
                                            domain=site.domain))

        msg = '{prefix}:SITE:END:{id}:{domain} - Site {i:04d} of {n:04d}'
        logger.info(msg.format(prefix=FPD_LOG_PREFIX,
                               id=site.id,
                               domain=site.domain,
                               i=i,
                               n=sites_count))

    msg = '{prefix}:END:date_for={date_for}, site_count={site_count}'
    logger.info(msg.format(prefix=FPD_LOG_PREFIX,
                           date_for=date_for,
                           site_count=sites_count))


#
# Daily Metrics Experimental Tasks
#


@shared_task
def experimental_populate_daily_metrics(date_for=None, force_update=False):
    '''Experimental task to populate daily metrics

    WARNING: In Ginkgo devstack, this task tends to gets stuck in the middle of
    processing course metrics. Not all the courses get processed and the site
    metrics doesn't get called.

    We're keeping it in the tasks so that we can continue to debug this.
    Enabling parallel course tasks will improve the pipeline performance

    '''
    def include_course(course_overview, threshold=50):
        '''This function let's us skip over courses with many enrollments, speeding
        up testing. Do not use for production
        '''
        count = CourseEnrollment.objects.filter(course_id=course_overview.id).count()
        return False if count > threshold else True

    if date_for:
        date_for = as_date(date_for)
    else:
        date_for = datetime.datetime.utcnow().replace(tzinfo=utc).date()
    date_for = date_for.strftime("%Y-%m-%d")
    logger.info(
        'Starting task "figures.experimental_populate_daily_metrics" for date "{}"'.format(
            date_for))

    courses = CourseOverview.objects.all()
    cdm_tasks = [
        populate_single_cdm.s(
            course_id=six.text_type(course.id),  # noqa: F821
            date_for=date_for,
            force_update=force_update) for course in courses if include_course(course)
    ]
    results = chord(cdm_tasks)(populate_single_sdm.s(
        date_for=date_for, force_update=force_update))

    # TODO: Are we going to update the SDM for the day if
    # * course records were created, meaning there are data not added to the SDM
    # * the SDM record already exists
    # * force_update is not true

    logger.info(
        'Finished task "figures.experimental_populate_daily_metrics" for date "{}"'.format(
            date_for))

    return results


#
# Monthly Metrics
#


@shared_task
def populate_course_mau(site_id, course_id, month_for=None, force_update=False):
    """Populates the MAU for the given site, course, and month
    """
    if month_for:
        month_for = as_date(month_for)
    else:
        month_for = datetime.datetime.utcnow().date()
    site = Site.objects.get(id=site_id)
    start_time = time.time()
    obj, _created = collect_course_mau(site=site,
                                       courselike=course_id,
                                       month_for=month_for,
                                       overwrite=force_update)
    if not obj:
        msg = 'populate_course_mau failed for course {course_id}'.format(
            course_id=str(course_id))
        logger.error(msg)
    elapsed_time = time.time() - start_time
    logger.info('populate_course_mau Elapsed time (seconds)={}. cdm_obj={}'.format(
        elapsed_time, obj))


@shared_task
def populate_mau_metrics_for_site(site_id, month_for=None, force_update=False):
    """
    Collect (save) MAU metrics for the specified site

    Iterates over all courses in the site to collect MAU counts
    TODO: Decide how sites would be excluded and create filter
    TODO: Check results of 'store_mau_metrics' to log unexpected results
    """
    site = Site.objects.get(id=site_id)
    msg = 'Starting figures'
    logger.info(msg)
    for course_id in site_course_ids(site):
        # 'course_id' should be string and not a CourseKey
        # However, we cast to 'str' so that this function doesn't care whether
        # the course identifier is a CourseKey type or a string
        populate_course_mau(site_id=site_id,
                            course_id=str(course_id),
                            month_for=month_for,
                            force_update=force_update)


@shared_task
def populate_all_mau():
    """
    Top level task to kick off MAU collection

    Initially, run it every day to observe monthly active user accumulation for
    the month and evaluate the results
    """
    for site in get_sites():
        populate_mau_metrics_for_site(site_id=site.id, force_update=False)


@shared_task
def populate_monthly_metrics_for_site(site_id):
    try:
        site = Site.objects.get(id=site_id)
        msg = 'Ran populate_monthly_metrics_for_site. [{}]:{}'
        with log_exec_time(msg.format(site.id, site.domain)):
            fill_last_smm_month(site=site)
    except Site.DoesNotExist:
        msg = '{prefix}:SITE:ERROR: site_id:{site_id} Site does not exist'
        logger.error(msg.format(prefix=FPM_LOG_PREFIX, site_id=site_id))
    except Exception:  # pylint: disable=broad-except
        msg = '{prefix}:SITE:ERROR: site_id:{site_id} Other error'
        logger.exception(msg.format(prefix=FPM_LOG_PREFIX, site_id=site_id))


@shared_task
def run_figures_monthly_metrics():
    """
    Populate monthly metrics for all sites.
    """
    if waffle.switch_is_active(WAFFLE_DISABLE_PIPELINE):
        logger.info('Figures pipeline is disabled due to %s being active.',
                    WAFFLE_DISABLE_PIPELINE)
        return

    logger.info('Starting figures.tasks.run_figures_monthly_metrics...')
    all_sites_jobs = group(populate_monthly_metrics_for_site.s(site.id) for site in get_sites())
    all_sites_jobs.delay()
