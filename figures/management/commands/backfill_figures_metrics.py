"""Backfills Figures historical metrics

"""

from __future__ import print_function

from __future__ import absolute_import
from textwrap import dedent

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from figures.backfill import backfill_monthly_metrics_for_site
from figures.sites import get_sites


def get_site(identifier):
    """Quick-n-dirty function to let the caller choose the site id or domain
    Let the 'get' fail if record can't be found from the identifier
    """
    try:
        filter_arg = dict(pk=int(identifier))
    except ValueError:
        filter_arg = dict(domain=identifier)
    return Site.objects.get(**filter_arg)


def backfill_site(site, overwrite):

    print('Backfilling monthly metrics for site id="{}" domain={}'.format(
        site.id,
        site.domain))
    backfilled = backfill_monthly_metrics_for_site(site=site,
                                                   overwrite=overwrite)
    if backfilled:
        for rec in backfilled:
            obj = rec['obj']
            print('Backfilled site "{}" for {} with active user count {}'.format(
                obj.site.domain,
                obj.month_for,
                obj.active_user_count))
    else:
        print('No student modules for site "{}"'.format(site.domain))


class Command(BaseCommand):
    """Populate Figures metrics models

    Improvements
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
        print('BEGIN: Backfill Figures Metrics')

        if options['site']:
            sites = [get_site(options['site'])]
        else:
            sites = get_sites()
        for site in sites:
            backfill_site(site, overwrite=options['overwrite'])

        print('DONE: Backfill Figures Metrics')
