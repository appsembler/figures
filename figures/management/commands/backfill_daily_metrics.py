'''Management command to manually populate course metrics

see the model ``edx_figures.models.CourseDailyMetrics``
'''

from __future__ import print_function

from __future__ import absolute_import

import datetime
from dateutil.rrule import rrule, DAILY
from textwrap import dedent

from figures.tasks import (
    populate_daily_metrics,
    experimental_populate_daily_metrics
)

from . import BaseBackfillCommand


class Command(BaseBackfillCommand):
    '''Populate Figures daily metrics models
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
        super(Command, self).add_arguments(self)

    def handle(self, *args, **options):
        '''
        Note the '# pragma: no cover' lines below. This is because we are not
        yet mocking celery for test coverage
        '''
        date_start = options['date_start'] or datetime.date.today()
        date_end = options['date_end'] or datetime.date.today()

        experimental = options['experimental']
        options.pop('experimental')

        print('BEGIN RANGE: Backfilling Figures daily metrics for dates {} to {}'.format(date_start, date_end))

        # populate daily metrics one day at a time for date range
        for dt in rrule(DAILY, dtstart=date_start, until=date_end):

            print('BEGIN: Backfill Figures daily metrics metrics for: '.format(dt))

            kwargs = dict(
                sites=self.get_sites(options['site']),
                date_for=dt,
                force_update=options['overwrite']
            )

            metrics_func = experimental_populate_daily_metrics if experimental else populate_daily_metrics
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

            print('END: Backfill Figures daily metrics metrics for: '.format(options['date'] or 'today'))

        print('END RANGE: Backfilling Figures daily metrics for dates {} to {}'.format(date_start, date_end))
