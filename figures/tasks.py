
import datetime
from django.utils.timezone import utc

from celery.app import shared_task
from tempfile import NamedTemporaryFile

from figures.helpers import as_date
from figures.serializers import CourseDailyMetricsSerializer
from figures.pipeline.course_daily_metrics import (
    CourseDailyMetricsLoader,
    CourseDailyMetricsJob,
)
from figures.pipeline.site_daily_metrics import (
    SiteDailyMetricsJob)


@shared_task
def write_tempfile(prefix='figures-test-', msg=None):
    '''
    Diagnostic task as a fast way to test celery and scheduling in devstack

    It creates a file in ``/tmp``
    '''
    if not msg:
        msg = 'apples and bananas'
    print('figures.tasks.write_tempfile called. msg={}'.format(msg))
    with  NamedTemporaryFile(delete=False, prefix=prefix, suffix=".txt") as fp:
        fp.write('{} - {}\n'.format(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            msg))

# TODO: Find or create a date string to date object decorator
@shared_task
def populate_cdm(course_id, date_for=None):
    if date_for:
        date_for = as_date(date_for)

    cdm_obj, created = CourseDailyMetricsLoader(course_id).load(date_for)
    cdm_data = CourseDailyMetricsSerializer(cdm_obj).data
    return dict(cdm=cdm_data, created=created)


@shared_task
def populate_daily_metrics(date_for=None, force_update=False):
    '''
    TODO: Improve error handling and capture failures
    '''
    print('task populate_daily_metrics called')
    if date_for:
        date_for = as_date(date_for)
    else:
        date_for = datetime.datetime.utcnow().replace(tzinfo=utc).date()

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

    print('done poulating daily metrics')
    # TODO return serialized results
    # We probably want to return ids, created flags and errors
