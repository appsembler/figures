'''

'''

import datetime

from django.contrib.auth import get_user_model
#from django.db.models import Avg, Count, F, Max, Sum
from django.db.models import Sum

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)

from figures.helpers import as_course_key, as_date, next_day, prev_day
from figures.models import CourseDailyMetrics, SiteDailyMetrics
from figures.pipeline.course_daily_metrics import (
    get_num_enrolled_in_exclude_admins,
    )

def get_active_user_count_for_date(date_for, course_daily_metrics=None):
    '''

    Do we have course daily metrics for the date_for?
    If so, we can use the data there,
    else, we need to calculate it
    '''
    aggregates = CourseDailyMetrics.objects.filter(date_for=date_for).aggregate(
        Sum('active_learners_today'))
    if aggregates and 'active_learners_today__sum' in aggregates:

        todays_active_user_count = aggregates['active_learners_today__sum'] or 0

        #import pdb; pdb.set_trace()
    else:
        todays_active_user_count = 0
    return todays_active_user_count

def get_previous_cumulative_active_user_count(date_for, site_daily_metrics=None):
        '''
        Collect from previous site daily metrics + today's course daily metrics

        This metric needs work. If the same user is active for 3 consecutive days
        is that a count of 1 or 3?

        So we're just going to be quick-n-dirty just to get something and sort
        it out later

        TODO: When adding 'site' to the SiteDailyMetrics model, change this to
        filter on the date_for instead of using a get
        '''

        if not site_daily_metrics:
            site_daily_metrics = SiteDailyMetrics.objects.all()
        aggregates = site_daily_metrics.filter(date_for=prev_day(date_for)).aggregate(
            Sum('cumulative_active_user_count'))

        return aggregates.get('cumulative_active_user_count',0)



def get_total_enrollment_count(date_for, course_overviews=None):
        '''
        Not including staff, admin, coaches, so using CourseEnrollmentManager's
        ``num_enrolled_in_exclude_admins`` method

        We could be a bit more elegant about this, doing a list comprehension 
        '''
        #qs = self.course_enrollments.filter(created__lt=next_day(date_for)).count()
        if not course_overviews:
            course_overviews = CourseOverview.objects.all()
        check_count = 0
        for co in course_overviews:
            check_count += get_num_enrolled_in_exclude_admins(
                course_id=co.id,
                date_for=date_for,
                )

        count = sum(get_num_enrolled_in_exclude_admins(
            as_course_key(id),
            date_for=date_for,
            ) for id in CourseOverview.objects.filter().values_list('id', flat=True))

        assert count == check_count, (
            'get_total_enrollment_count: mismatched numbers. count={}, check_count={}'.format(count, check_count)
            )
        return count

class SiteDailyMetricsExtractor(object):
    '''

    '''
    def __init__(self):
        pass

    def extract(self, date_for=None, **kwargs):
        if not date_for:
            date_for = prev_day(datetime.datetime.utcnow().date())

        data = dict()

        user_count = get_user_model().objects.filter(
            date_joined__lt=next_day(date_for)).count()
        course_count = CourseOverview.objects.filter(
            enrollment_start__lt=next_day(date_for)).count()

        todays_active_user_count = get_active_user_count_for_date(date_for)
        data['todays_active_user_count'] = todays_active_user_count

        #import pdb; pdb.set_trace()

        data['cumulative_active_user_count'] = get_previous_cumulative_active_user_count(
            date_for) + todays_active_user_count
        data['total_user_count'] = user_count
        data['course_count'] = course_count
        data['total_enrollment_count'] = get_total_enrollment_count(date_for)
        return data


class SiteDailyMetricsLoader(object):

    def __init__(self):
        self.extractor = SiteDailyMetricsExtractor()

    def load(self, date_for=None, **kwargs):
        '''
        TODO: Add filtering for
        * Multi-tenancy
        * Course acess groups
        '''
        if not date_for:
            date_for = prev_day(datetime.datetime.utcnow().date())

        data = self.extractor.extract(date_for=date_for)

        site_metrics, created = SiteDailyMetrics.objects.update_or_create(
            date_for=date_for,
            defaults=dict(
                cumulative_active_user_count=data['cumulative_active_user_count'],
                todays_active_user_count=data['todays_active_user_count'],
                total_user_count=data['total_user_count'],
                course_count=data['course_count'],
                total_enrollment_count=data['total_enrollment_count'],
            )
        )

        return site_metrics, created


class SiteDailyMetricsJob(object):

    @classmethod
    def run(self, *args, **kwargs):
        results = SiteDailyMetricsLoader().load()
        return results
