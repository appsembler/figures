
import datetime
from django.utils.timezone import utc

from celery.app import shared_task
from celery.utils.log import get_task_logger

from figures.helpers import as_date
from figures.serializers import CourseDailyMetricsSerializer
from figures.pipeline.course_daily_metrics import (
    CourseDailyMetricsLoader,
    CourseDailyMetricsJob,
)
from figures.pipeline.site_daily_metrics import (
    SiteDailyMetricsJob)

logger = get_task_logger(__name__)


# TODO: Find or create a date string to date object decorator
@shared_task
def populate_cdm(course_id, date_for=None):
    if date_for:
        date_for = as_date(date_for)

    cdm_obj, created = CourseDailyMetricsLoader(course_id).load(date_for)


@shared_task
def populate_daily_metrics(date_for=None, force_update=False):
    '''
    TODO: Add error handling and error logging
    TODO: chain the site daily metrics job after all the course daily metrics
    jobs have finished. This is because for the given day, the site daily metrics
    aggregates data from all the site's course daily metrics
    '''
    if date_for:
        date_for = as_date(date_for)
    else:
        date_for = datetime.datetime.utcnow().replace(tzinfo=utc).date()

    logger.info('Starting task "figures.populate_daily_metrics" for date "{}"'.format(
        date_for))

    cdm_results = CourseDailyMetricsJob.run(
        date_for=date_for,
        force_update=force_update,
        )

    # TODO: Are we going to update the SDM for the day if
    # * course records were created, meaning there are data not added to the SDM
    # * the SDM record already exists
    # * force_update is not true

    sdm_results = SiteDailyMetricsJob.run(
        date_for=date_for,
        force_update=force_update,
        )

    logger.info('Finished task "figures.populate_daily_metrics" for date "{}"'.format(
        date_for))
