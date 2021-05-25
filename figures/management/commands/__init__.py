"""
Management commands for Figures.
"""
from datetime import datetime

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from figures import helpers
from figures.sites import get_sites


class BaseBackfillCommand(BaseCommand):
    '''Base class for Figures backfill management commands with common options.
    '''
    def get_sites(self, identifier=None):
        """Quick-n-dirty function to let the caller choose the site id or domain.
        If no identifier is passed, return all available Sites.
        Let the 'get' fail if record can't be found from the identifier.
        """
        if not identifier:
            return get_sites()
        else:
            try:
                filter_arg = dict(pk=int(identifier))
            except ValueError:
                filter_arg = dict(domain=identifier)
            return Site.objects.filter(**filter_arg)

    def get_date(self, date_str=None):
        '''Return a datetime.date from a string or NoneType.
        '''
        try:
            return helpers.as_date(date_str)
        except TypeError:
            return datetime.today().date()

    def add_arguments(self, parser):
        '''
        '''
        parser.add_argument(
            '--site',
            help='backfill a specific site. provide numeric id or domain name',
            default=None
        )
        # TODO: handle date start later than date end
        parser.add_argument(
            '--date_start',
            help='date for which we start backfilling data',
        )
        parser.add_argument(
            '--date_end',
            help='date for which we end backfilling data',
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
