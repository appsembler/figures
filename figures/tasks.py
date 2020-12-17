'''
Figures Celery tasks. Initially this module contains tasks for the ETL pipeline.

'''
from __future__ import absolute_import
import datetime
import time

from django.contrib.sites.models import Site
from django.utils.timezone import utc

from celery import chord
from celery.app import shared_task
from celery.utils.log import get_task_logger

# TODO: import CourseOverview from figures.compat
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview  # noqa pylint: disable=import-error
from student.models import CourseEnrollment  # pylint: disable=import-error

from figures.backfill import backfill_enrollment_data_for_site
from figures.helpers import as_course_key, as_date
from figures.log import log_exec_time
from figures.models import PipelineError
from figures.pipeline.course_daily_metrics import CourseDailyMetricsLoader
from figures.pipeline.site_daily_metrics import SiteDailyMetricsLoader
import figures.sites
from figures.pipeline.mau_pipeline import collect_course_mau
from figures.pipeline.site_monthly_metrics import fill_last_month as fill_last_smm_month
from figures.pipeline.logger import log_error_to_db
import six


logger = get_task_logger(__name__)


# For debugging in the devstack celery worker, unremark this line
# This can reduce the noise over seting the log level to info via the Celery
# worker command line, ``./manage.py celery worker -l INFO --settings=devstack``
#
# TODO: Make this configurable in the settings
# logger.setLevel('INFO')


@shared_task
def populate_single_cdm(course_id, date_for=None, force_update=False):
    '''Populates a CourseDailyMetrics record for the given date and course

    TODO: cdm needs to handle course_id as the string
    '''
    if date_for:
        date_for = as_date(date_for)

    # Provide info in celery log
    learner_count = CourseEnrollment.objects.filter(
        course_id=as_course_key(course_id)).count()
    msg = 'populate_single_cdm. course id = "{}", learner count={}'.format(
        course_id, learner_count)
    logger.info(msg)

    start_time = time.time()

    cdm_obj, _created = CourseDailyMetricsLoader(
        course_id).load(date_for=date_for, force_update=force_update)
    elapsed_time = time.time() - start_time
    logger.info('done. Elapsed time (seconds)={}. cdm_obj={}'.format(
        elapsed_time, cdm_obj))


@shared_task
def populate_site_daily_metrics(site_id, **kwargs):
    '''Populate a SiteDailyMetrics record
    '''
    logger.debug(
        'populate_site_daily_metrics called for site_id={}'.format(site_id))
    SiteDailyMetricsLoader().load(
        site=Site.objects.get(id=site_id),
        date_for=kwargs.get('date_for', None),
        force_update=kwargs.get('force_update', False),
        )
    logger.debug(
        'done running populate_site_daily_metrics for site_id={}'.format(site_id))


@shared_task
def update_enrollment_data(site_id, **_kwargs):
    """
    This can be an expensive task as it iterates over all th
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
        msg = ('FIGURES:FAIL daily metrics:update_enrollment_data'
               ' for site_id={}'.format(site_id))
        logger.exception(msg)


@shared_task
def populate_daily_metrics(date_for=None, force_update=False):
    '''Populates the daily metrics models for the given date

    This method populates CourseDailyMetrics for all the courses in the site,
    then populates SiteDailyMetrics

    It calls the individual tasks, ``populate_single_cdm`` and
    ``populate_site_daily_metrics`` as immediate calls so that no courses are
    missed when the site daily metrics record is populated.

    NOTE: We have an experimental task that runs the course populators in

    parallel, then when they are all done, populates the site metrics. See the
    function ``experimental_populate_daily_metrics`` docstring for details

    TODO: Add error handling and error logging
    TODO: Create and add decorator to assign 'date_for' if None
    '''
    if date_for:
        date_for = as_date(date_for)
    else:
        date_for = datetime.datetime.utcnow().replace(tzinfo=utc).date()

    logger.info('Starting task "figures.populate_daily_metrics" for date "{}"'.format(
        date_for))

    sites_count = Site.objects.count()
    for i, site in enumerate(Site.objects.all()):
        try:
            for course in figures.sites.get_courses_for_site(site):
                try:
                    populate_single_cdm(
                        course_id=course.id,
                        date_for=date_for,
                        force_update=force_update)
                except Exception as e:  # pylint: disable=broad-except
                    logger.exception('figures.tasks.populate_daily_metrics failed')
                    # Always capture CDM load exceptions to the Figures pipeline
                    # error table
                    error_data = dict(
                        date_for=date_for,
                        msg='figures.tasks.populate_daily_metrics failed',
                        exception_class=e.__class__.__name__,
                        )
                    if hasattr(e, 'message_dict'):
                        error_data['message_dict'] = e.message_dict  # pylint: disable=no-member
                    log_error_to_db(
                        error_data=error_data,
                        error_type=PipelineError.COURSE_DATA,
                        course_id=str(course.id),
                        site=site,
                        logger=logger,
                        log_pipeline_errors_to_db=True,
                        )
            populate_site_daily_metrics(
                site_id=site.id,
                date_for=date_for,
                force_update=force_update)

            # Until we implement signal triggers
            try:
                update_enrollment_data(site_id=site.id)
            except Exception:  # pylint: disable=broad-except
                msg = ('FIGURES:FAIL figures.tasks update_enrollment_data '
                       ' unhandled exception. site[{}]:{}')
                logger.exception(msg.format(site.id, site.domain))

        except Exception:  # pylint: disable=broad-except
            msg = ('FIGURES:FAIL populate_daily_metrics unhandled site level'
                   ' exception for site[{}]={}')
            logger.exception(msg.format(site.id, site.domain))
        logger.info("figures.populate_daily_metrics: finished Site {:04d} of {:04d}".format(
            i, sites_count))
    logger.info('Finished task "figures.populate_daily_metrics" for date "{}"'.format(
        date_for))


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
    results = chord(cdm_tasks)(populate_site_daily_metrics.s(
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
    for course_key in figures.sites.get_course_keys_for_site(site):
        populate_course_mau(site_id=site_id,
                            course_id=str(course_key),
                            month_for=month_for,
                            force_update=force_update)


@shared_task
def populate_all_mau():
    """
    Top level task to kick off MAU collection

    Initially, run it every day to observe monthly active user accumulation for
    the month and evaluate the results
    """
    for site in Site.objects.all():
        populate_mau_metrics_for_site(site_id=site.id, force_update=False)


@shared_task
def populate_monthly_metrics_for_site(site_id):

    site = Site.objects.get(id=site_id)
    msg = 'Ran populate_monthly_metrics_for_site. [{}]:{}'
    with log_exec_time(msg.format(site.id, site.domain)):
        fill_last_smm_month(site=site)


@shared_task
def run_figures_monthly_metrics():
    """
    TODO: only run for active sites. Requires knowing which sites we can skip
    """
    logger.info('Starting figures.tasks.run_figures_monthly_metrics...')
    for site in Site.objects.all():
        populate_monthly_metrics_for_site.delay(site_id=site.id)
