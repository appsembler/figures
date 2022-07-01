'''Management command to manually populate course and site daily metrics

See the models ``figures.models.CourseDailyMetrics`` and ``figures.models.SiteDailyMetrics``
'''

from __future__ import print_function

from __future__ import absolute_import

from textwrap import dedent

from dateutil.rrule import rrule, DAILY

from django.core.management.base import BaseCommand, CommandError

from figures.helpers import as_date
from figures.sites import Site
from figures.pipeline.backfill import backfill_daily_metrics_for_site_and_date


class Command(BaseCommand):
    '''Populate Figures daily metrics models (``CourseDailyMetrics`` and ``SiteDailyMetrics``).
    Note that correctly populating cumulative user and course count for ``SiteDailyMetrics``
    relies on running this sequentially forward from the first date for which StudentModule records
    are present.
    '''

    help = dedent(__doc__).strip()

    def do_backfill(self, site, date_for, **kwargs):
        """Thin wrapper around backfill function to handle parameters
        """
        if kwargs.get('skip_sdm', False):
            process_sdm = False
        else:
            process_sdm = True
        logdir = kwargs.get('logdir', None)
        force_update = kwargs.get('force_update', False)

        return backfill_daily_metrics_for_site_and_date(site,
                                                        date_for,
                                                        process_sdm=process_sdm,
                                                        logdir=logdir,
                                                        force_update=force_update)

    def get_site(self, options):
        """Return a Site object matching the command line arg

        The 'site' option can be a domain name (sans protocol) or the site
        record primary key
        """
        identifier = options['site']
        try:
            filter_arg = dict(pk=int(identifier))
        except ValueError:
            filter_arg = dict(domain=identifier)
        return Site.objects.get(**filter_arg)

    def get_dates(self, options):
        """Return a list of dates
        """
        if options['date'] and options['date_range']:
            raise CommandError(
                'Select either "--date" or "--date-range" option, but not both')
        if not options['date'] and not options['date_range']:
            raise CommandError(
                'You need to select one of "--date" or "--date-range" parameters')
        if options['date']:
            return [as_date(options['date'])]
        else:
            dates = sorted([as_date(rec) for rec in options['date_range']])
            # The '--date-range' CLI argument enforces two values
            return [dt.date() for dt in rrule(freq=DAILY,
                                              dtstart=dates[0],
                                              until=dates[1])]

    def add_arguments(self, parser):
        parser.add_argument('site', help='Site domain or id')

        parser.add_argument('--date', help='Run backfill for a single date')
        parser.add_argument('--date-range', nargs=2,
                            help='Run backfill from a start date to an end date')

        # by default we process the SDM. If we do not want to, set this flag
        parser.add_argument('--skip-sdm', action='store_true',
                            help='Set this flag to avoid collecting SDM records')
        parser.add_argument('--force-update', action='store_true',
                            help='Update records if they already exist')
        parser.add_argument('--logdir', default=None,
                            help='altnerate path to output log files')

    def handle(self, *args, **options):
        site = self.get_site(options)
        dates = self.get_dates(options)
        backfill_options = ['skip_sdm', 'force_update', 'logdir']
        extra_args = dict((key, options[key]) for key in backfill_options)
        # import pdb; pdb.set_trace()

        for date_for in dates:
            print('Generating daily metrics for date: {}'.format(date_for.isoformat()))
            results = self.do_backfill(site=site,
                                       date_for=date_for,
                                       **extra_args)
            print('Finished date {}. Processed {} courses'.format(
                date_for.isoformat(), results['courses_processed']))
            print('Wrote log file: "{}"'.format(results['logfile']))
            print('CDM processing time: {}, SDM processing time: {}'.format(
                results['cdms_elapsed'], results['sdm_elapsed']))
