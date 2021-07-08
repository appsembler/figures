'''Management command to manually populate course and site daily metrics

See the models ``figures.models.CourseDailyMetrics`` and ``figures.models.SiteDailyMetrics``
'''

from __future__ import print_function

from __future__ import absolute_import

from textwrap import dedent

from dateutil.rrule import rrule, DAILY

from figures.management.base import BaseBackfillCommand
from figures.tasks import (
    populate_daily_metrics,
    experimental_populate_daily_metrics
)


class Command(BaseBackfillCommand):
    '''Populate Figures daily metrics models (``CourseDailyMetrics`` and ``SiteDailyMetrics``).
    Note that correctly populating cumulative user and course count for ``SiteDailyMetrics``
    relies on running this sequentially forward from the first date for which StudentModule records
    are present.
    '''

    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        parser.add_argument(
            '--experimental',
            action='store_true',
            default=False,
            help=('Run with Celery workflows (Warning: This is still under'
                  ' development and likely to get stuck/hung jobs')
        )
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        '''
        Note the '# pragma: no cover' lines below. This is because we are not
        yet mocking celery for test coverage
        '''
        date_start = self.get_date(options['date_start'])
        date_end = self.get_date(options['date_end'])

        experimental = options['experimental']

        print('BEGIN RANGE: Backfilling Figures daily metrics for dates {} to {}'.format(
            date_start, date_end
        ))

        # don't pass multiple site ids to tasks
        site_id = None if not options['site'] else self.get_site_ids(options['site'])

        # populate daily metrics one day at a time for date range
        for dt in rrule(DAILY, dtstart=date_start, until=date_end):

            print('BEGIN: Backfill Figures daily metrics metrics for: {}'.format(dt))

            kwargs = dict(
                site_id=site_id,
                date_for=str(dt),
                force_update=options['overwrite']
            )

            if experimental:
                metrics_func = experimental_populate_daily_metrics
                del kwargs['site_id']  # not implemented for experimental
            else:
                metrics_func = populate_daily_metrics
            # try:
            if options['no_delay']:
                metrics_func(**kwargs)
            else:
                metrics_func.delay(**kwargs)  # pragma: no cover
            # except Exception as e:  # pylint: disable=bare-except
            #     if options['ignore_exceptions']:
            #         self.print_exc("daily", dt, e.message)
            #     else:
            #         raise

            print('END: Backfill Figures daily metrics metrics for: {}'.format(dt))

        print('END RANGE: Backfilling Figures daily metrics for dates {} to {}'.format(
            date_start, date_end
        ))
