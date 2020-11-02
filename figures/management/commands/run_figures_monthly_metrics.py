"""Figures management command to manually start Celery tasks from the shell

We're starting with the monthly metrics
"""

from __future__ import print_function

from __future__ import absolute_import
from textwrap import dedent

from django.core.management.base import BaseCommand

from figures.tasks import (
    run_figures_monthly_metrics
)


class Command(BaseCommand):
    """Task runner to kick off Figures celery tasks
    """
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        parser.add_argument('--no-delay',
                            action='store_true',
                            default=False,
                            help='Disable the celery "delay" directive')

    def handle(self, *args, **options):
        print('Starting Figures monthly metrics...')

        if options['no_delay']:
            run_figures_monthly_metrics()
        else:
            run_figures_monthly_metrics.delay()

        print('Done.')
