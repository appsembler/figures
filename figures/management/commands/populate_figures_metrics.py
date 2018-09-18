'''Management command to manually populate course metrics

see the model ``edx_figures.models.CourseDailyMetrics``
'''

from __future__ import print_function

import datetime
from textwrap import dedent

from dateutil.parser import parse as dateutil_parse

from django.core.management.base import BaseCommand, CommandError

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)

from figures.pipeline.jobs import AllDailyMetricsJob


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

    def handle(self, *args, **options):
        print('populating Figures metrics')
        if options['date']:
            date_for = dateutil_parse(options['date'])
        else:
            date_for = None

        # TODO: Enable running as celery task

        job = AllDailyMetricsJob(date_for=date_for)
        results = job.run()
        print('Done populating course metrics for day {}'.format(date_for))
        
        #print('inspect me')
        #import pdb; pdb.set_trace()
