"""
Management command base classes for Figures.
"""
from datetime import datetime

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from figures import helpers
from figures.sites import get_sites


class BaseBackfillCommand(BaseCommand):
    '''Base class for Figures backfill management commands with common options.
    '''
    def get_site_ids(self, identifier=None):
        """Quick-n-dirty function to let the caller choose the site id or domain.
        If no identifier is passed, return all available Sites.
        Let the 'get' fail if record can't be found from the identifier.
        Returns Site ids for passing to Celery tasks.
        Note that at present, none of the tasks handle more than one specified Site.
        """
        if not identifier:
            sites = get_sites()
        else:
            try:
                filter_arg = dict(pk=int(identifier))
            except ValueError:
                filter_arg = dict(domain=identifier)
            sites = Site.objects.filter(**filter_arg)
        return [site.id for site in sites]

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
        # TODO: allow passing the queue to use.  Warn if no_delay specified.
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

    def print_exc(self, metrics_type, date, exc_message):
        print("Could not populate {} for {}. Exception was {}".format(
            metrics_type, date, exc_message)
        )
