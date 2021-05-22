"""Backfills Figures historical metrics

"""

from __future__ import print_function

from __future__ import absolute_import

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
    """Backfill Figures monthly metrics models.
    """
    def handle(self, *args, **options):
        print('BEGIN: Backfill Figures Monthly Metrics')

        if options['site']:
            sites = [get_site(options['site'])]
        else:
            sites = get_sites()
        for site in sites:
            backfill_site(site, overwrite=options['overwrite'])

        print('END: Backfill Figures Metrics')
