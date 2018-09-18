'''Management command to manually populate course metrics

see the model ``edx_figures.models.CourseDailyMetrics``
'''

from __future__ import print_function

import datetime
from textwrap import dedent

from dateutil.parser import parse as dateutil_parse

from django.core.management.base import BaseCommand, CommandError


from figures.tasks import populate_daily_metrics


class Command(BaseCommand):
    '''Populate Figures metrics models

    '''

    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        '''

        TODO: Add option to list courses
        '''

        parser.add_argument('--date',
                            help='date for which we are retrieving data in yyyy-mm-dd format')
        parser.add_argument('--no-delay',
                            action='store_true',
                            default=False,
                            help='Disable the celery "delay" directive')

    def handle(self, *args, **options):
        print('populating Figures metrics')
        if options['date']:
            date_for = dateutil_parse(options['date'])
        else:
            date_for = None

        # TODO: Enable running as celery task

        if options['no_delay']:
            results = populate_daily_metrics(date_for=date_for)
        else:
            results = populate_daily_metrics.delay(date_for=date_for)
        print('Management command populate_figures_metrics complete. date_for: {}'.format(
            date_for))
