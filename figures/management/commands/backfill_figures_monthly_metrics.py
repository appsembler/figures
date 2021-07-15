"""Backfills Figures historical metrics

"""

from __future__ import print_function
from __future__ import absolute_import

from textwrap import dedent

from django.contrib.sites.models import Site

from figures.backfill import backfill_monthly_metrics_for_site
from figures.management.base import BaseBackfillCommand


def backfill_site(site, overwrite, use_raw_sql):

    print('Backfilling monthly metrics for site id={} domain={}'.format(
        site.id,
        site.domain))
    backfilled = backfill_monthly_metrics_for_site(site=site,
                                                   overwrite=overwrite,
                                                   use_raw_sql=use_raw_sql)
    if backfilled:
        for rec in backfilled:
            obj = rec['obj']
            print('Backfilled site "{}" for {} with active user count {}'.format(
                obj.site.domain,
                obj.month_for,
                obj.active_user_count))
    else:
        print('No student modules for site "{}"'.format(site.domain))


class Command(BaseBackfillCommand):
    """Backfill Figures monthly metrics models.
    """
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        '''
        '''
        parser.add_argument(
            '--use_raw_sql',
            help=('Use raw SQL for query performance with large number of StudentModules, '
                  'where supported.'),
            default=False,
            action="store_true"
        )
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        print('BEGIN: Backfill Figures Monthly Metrics')

        for site_id in self.get_site_ids(options['site']):
            site = Site.objects.get(id=site_id)
            backfill_site(site, overwrite=options['overwrite'], use_raw_sql=options['use_raw_sql'])

        print('END: Backfill Figures Metrics')
