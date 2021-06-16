"""Figures management command to run course MAU metrics for all courses, all Sites.
"""

from __future__ import print_function

from __future__ import absolute_import

from textwrap import dedent

from django.core.management.base import BaseCommand

from figures.tasks import (
    populate_all_mau
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
        print('Starting Figures MAU metrics for all Sites...')

        if options['no_delay']:
            populate_all_mau()
        else:
            populate_all_mau.delay()

        print('Done.')
