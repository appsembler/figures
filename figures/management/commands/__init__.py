"""
Management commands for Figures.
"""
import datetime
from textwrap import dedent

from django.core.management.base import BaseCommand


class BaseBackfillCommand(BaseCommand):
    '''Base class for Figures backfill management commands with common options.
    '''
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        '''
        '''
        parser.add_argument(
            '--site',
            help='backfill a specific site. provide id or domain name',
            default=None
        )
        parser.add_argument(
            '--date_start',
            help='date for which we start backfilling data, in yyyy-mm-dd format',
            action='store_true'
        )
        parser.add_argument(
            '--date_end',
            help='date for which we end backfilling data, in yyyy-mm-dd format',
            action='store_true'
        )
        parser.add_argument(
            '--no-delay',
            action='store_true',
            default=False,
            help='Disable the celery "delay" directive'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            default=False,
            help='Overwrite metrics records if they exist for the given date'
        )
        # parser.add_argument(
        #     '--ignore_exceptions',
        #     action='store_true',
        #     default=False,
        #     help='Print exceptions if thrown, and continue processing'
        # )

    def print_exc(metrics_type, date, exc_message):
        print("Could not populate {} for {}. Exception was {}".format(
            metrics_type, date, exc_message)
        )
