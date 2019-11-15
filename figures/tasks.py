'''
Figures Celery tasks. Initially this module contains tasks for the ETL pipeline.

'''
import datetime
import time

from django.contrib.sites.models import Site
from django.utils.timezone import utc

from celery import chord
from celery.app import shared_task
from celery.utils.log import get_task_logger

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from student.models import CourseEnrollment

from figures.helpers import as_course_key, as_date
from figures.mau import store_mau_metrics
from figures.models import PipelineError
from figures.pipeline.course_daily_metrics import CourseDailyMetricsLoader
from figures.pipeline.site_daily_metrics import SiteDailyMetricsLoader
import figures.sites
from figures.pipeline.logger import log_error_to_db


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

    cdm_obj, created = CourseDailyMetricsLoader(
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
        'done running populate_site_daily_metrics for site_id={}"'.format(site_id))


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

    for site in Site.objects.all():
        for course in figures.sites.get_courses_for_site(site):
            try:
                populate_single_cdm(
                    course_id=course.id,
                    date_for=date_for,
                    force_update=force_update)
            except Exception as e:
                logger.exception('figures.tasks.populate_daily_metrics failed')
                # Always capture CDM load exceptions to the Figures pipeline
                # error table
                error_data = dict(
                    date_for=date_for,
                    msg='figures.tasks.populate_daily_metrics failed',
                    exception_class=e.__class__.__name__,
                    )
                if hasattr(e, 'message_dict'):
                    error_data['message_dict'] = e.message_dict
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

    logger.info('Finished task "figures.populate_daily_metrics" for date "{}"'.format(
        date_for))


#
# Experimental tasks
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
            course_id=unicode(course.id),  # noqa: F821
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


@shared_task
def collect_mau_metrics_for_site(site_id, overwrite=False):
    """
    Collect (save) MAU metrics for the specified site
    TODO: Check results of 'store_mau_metrics' to log unexpected
    results
    """
    store_mau_metrics(site=Site.objects.get(id=site_id),
                      overwrite=overwrite)


@shared_task
def collect_mau_metrics(site_ids=None, overwrite=False, **kwargs):
    """
    Collect MAU metrics for either all sites or the specified sites
    """

    for site_id in figures.sites.site_id_iterator(site_ids or Site.objects.all()):
        collect_mau_metrics_for_site(site_id=site_id,
                                     overwrite=overwrite)


@shared_task
def run_month_end_jobs():
    """
    Placeholder task function. We may need to do a daily and
    check if we are at the end of the month
    Call this at the end of the month
    Call our end of month metrics collectors here
    """
    collect_mau_metrics()
