
import datetime

from celery.app import shared_task
from tempfile import NamedTemporaryFile

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


@shared_task
def populate_cdm(course_id, date_for=None):

    cdm_obj, created = CourseDailyMetricsLoader(course_id).load()
    cdm_data = CourseDailyMetricsSerializer(cdm_obj).data
    print('cdm data created: {}'.format(cdm_data))
    return dict(cdm=cdm_data, created=created)


@shared_task
def populate_daily_metrics(date_for=None):
    '''
    TODO: Improve error handling and capture failures
    '''
    print('task populate_metrics called')
    if not date_for:
        date_for = datetime.datetime.utcnow().date()
    result = CourseDailyMetricsJob.run(date_for)

