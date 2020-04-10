"""Backfills Figures historical metrics

"""

from __future__ import print_function

from textwrap import dedent

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from figures.backfill import backfill_monthly_metrics_for_site


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

    def handle(self, *args, **options):
        print('BEGIN: Backfill Figures Metrics')

        # Would be great to be able to filter out dead sites
        # Would be really great to be able to filter out dead sites
        # Would be really Really great to be able to filter out dead sites
        # Would be really Really REALLY great to be able to filter out dead sites
        overwrite = options['overwrite']
        for site in Site.objects.all():
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
        print('DONE: Backfill Figures Metrics')
