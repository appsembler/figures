'''Management command to manually populate course metrics

see the model ``edx_figures.models.CourseDailyMetrics``
'''

from __future__ import print_function

from __future__ import absolute_import
from textwrap import dedent

from django.core.management.base import BaseCommand

from figures.tasks import (
    populate_daily_metrics,
    experimental_populate_daily_metrics,
    populate_all_mau,
)


class Command(BaseCommand):
    '''Populate Figures metrics models
    '''
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        '''
        '''

        parser.add_argument('--date',
                            help='date for which we are retrieving data in yyyy-mm-dd format')
        parser.add_argument('--no-delay',
                            action='store_true',
                            default=False,
                            help='Disable the celery "delay" directive')
        parser.add_argument('--force-update',
                            action='store_true',
                            default=False,
                            help='Overwrite metrics records if they exist for the given date')
        parser.add_argument('--experimental',
                            action='store_true',
                            default=False,
                            help=('Run with Celery workflows (Warning: This is still under' +
                                  ' development and likely to get stuck/hung jobs'))
        parser.add_argument('--mau',
                            action='store_true',
                            default=False,
                            help='Run just the MAU pipeline')

    def handle(self, *args, **options):
        '''
        Note the '# pragma: no cover' lines below. This is because we are not
        yet mocking celery for test coverage

        The 'mau' conditional check in this method is a quick hack to run the
        MAU task from this command. What we probably want is a 'figures_cli'
        command with subcommands.
        '''
        print('populating Figures metrics...')

        kwargs = dict(
            date_for=options['date'],
            force_update=options['force_update'],
            )

        if options['mau']:
            if options['no_delay']:
                populate_all_mau()
            else:
                populate_all_mau.delay()  # pragma: no cover
        else:
            experimental = options['experimental']
            options.pop('experimental')

            if experimental:
                if options['no_delay']:
                    experimental_populate_daily_metrics(**kwargs)
                else:
                    experimental_populate_daily_metrics.delay(**kwargs)  # pragma: no cover
            else:
                if options['no_delay']:
                    populate_daily_metrics(**kwargs)
                else:
                    populate_daily_metrics.delay(**kwargs)  # pragma: no cover

        # TODO: improve this message to say 'today' when options['date'] is None
        print('Management command populate_figures_metrics complete. date_for: {}'.format(
            options['date']))
        print('Done.')
