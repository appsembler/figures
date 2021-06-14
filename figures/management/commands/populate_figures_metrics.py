"""
Deprecated:
Please call instead backfill_figures_daily_metrics.

Management command to manually populate course metrics

see the model ``edx_figures.models.CourseDailyMetrics``
"""

from __future__ import print_function

from __future__ import absolute_import
from textwrap import dedent
import warnings

from django.core.management import call_command
from django.core.management.base import BaseCommand


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
        Pending deprecation.  Passes handling off to new commands.

        The 'mau' conditional check in this method is a quick hack to run the
        MAU task from this command. What we probably want is a 'figures_cli'
        command with subcommands.
        '''
        warnings.warn(
            "populate_figures_metrics is pending deprecation and will be removed in "
            "Figures 1.0. Please use backfill_figures_daily_metrics, instead; or, "
            "if you were calling with --mau option, use populate_figures_mau_metrics.",
            PendingDeprecationWarning
        )
        print('populating Figures metrics...')

        if options['mau']:
            call_command('run_figures_mau_metrics', no_delay=options['no_delay'])
        else:
            call_command(
                'backfill_figures_daily_metrics',
                no_delay=options['no_delay'],
                date_start=options['date'],
                date_end=options['date'],
                overwrite=options['force_update'],
                experimental=options['experimental']
            )

        # TODO: improve this message to say 'today' when options['date'] is None
        print('Management command populate_figures_metrics complete. date_for: {}'.format(
            options['date']))
        print('Done.')
