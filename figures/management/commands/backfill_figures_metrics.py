"""Deprecated:
Please call instead one of:
backfill_figures_daily_metrics, backfill_figures_monthly_metrics, or
backfill_figures_enrollment_data

Backfills Figures historical metrics

"""

from __future__ import print_function

from __future__ import absolute_import
from textwrap import dedent
import warnings

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Pending Deprecation: Populate Figures metrics models
    """
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        parser.add_argument('--overwrite',
                            action='store_true',
                            default=False,
                            help='overwrite existing data in SiteMonthlyMetrics')
        parser.add_argument('--site',
                            help='backfill a specific site. provide id or domain name')

    def handle(self, *args, **options):
        '''
        Pending deprecation.  Passes handling off to new commands.
        '''
        warnings.warn(
            "backfill_figures_metrics is pending deprecation and will be removed in "
            "Figures 1.0. Please use one of backfill_figures_daily_metrics, "
            "backfill_figures_monthly_metrics, or backfill_figures_enrollment_data, "
            "instead.",
            PendingDeprecationWarning
        )
        print('BEGIN: Backfill Figures Metrics')

        call_command(
            'backfill_figures_monthly_metrics',
            overwrite=options['overwrite'],
            site=options['site']
        )
        call_command(
            'backfill_figures_daily_metrics',
            overwrite=options['overwrite'],
            site=options['site']
        )

        print('DONE: Backfill Figures Metrics')
