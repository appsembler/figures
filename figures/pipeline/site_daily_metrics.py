'''This module populates the figures.models.SiteDailyMetrics model


Most of the data are from CourseDailyMetrics. Some data are not captured in 
course metrics. These data are extracted directly from edx-platform models

'''

import datetime

from django.utils.timezone import utc
from django.contrib.auth import get_user_model
from django.db.models import Sum, Value

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
    else, we need to calculate it or raise that we don't have data we need
    '''
    aggregates = CourseDailyMetrics.objects.filter(date_for=date_for).aggregate(
        Sum('active_learners_today'))
    if aggregates and 'active_learners_today__sum' in aggregates:
        todays_active_user_count = aggregates['active_learners_today__sum'] or 0
    else:
        todays_active_user_count = 0
    return todays_active_user_count


def get_previous_cumulative_active_user_count(date_for):
        ''' Returns the cumulative site-wide active user count for the previous day

        This is a simple helper function that returns the cumulative active user
        count for the day before the given date. Returns 0 if there is no
        record for the previous day
        '''
        try:
            return SiteDailyMetrics.objects.get(
                date_for=prev_day(date_for)).cumulative_active_user_count or 0
        except SiteDailyMetrics.DoesNotExist:
            return 0


def get_total_enrollment_count(date_for, course_ids=None):
    '''Returns the total enrollments across all courses for the site
    It does not return unique learners
    '''
    aggregates = CourseDailyMetrics.objects.filter(date_for=date_for).aggregate(
        Sum('enrollment_count'))
    if aggregates and 'enrollment_count__sum' in aggregates:
        enrollment_count = aggregates['enrollment_count__sum'] or 0
    else:
        enrollment_count = 0
    return enrollment_count


class SiteDailyMetricsExtractor(object):
    '''
    Currently a bag of "function". We can change this to a function if we
    decide we don't need state
    '''
    def __init__(self):
        pass

    def extract(self, date_for=None, **kwargs):
        '''
        We get the count from the User model since there can be registered users
        who have not enrolled.

        TODO: Exclude non-students from the user count
        '''
        if not date_for:
            date_for = prev_day(
                datetime.datetime.utcnow().replace(tzinfo=utc).date()
                )

        data = dict()

        user_count = get_user_model().objects.filter(
            date_joined__lt=next_day(date_for)).count()
        course_count = CourseOverview.objects.filter(
            enrollment_start__lt=next_day(date_for)).count()

        todays_active_user_count = get_active_user_count_for_date(date_for)
        data['todays_active_user_count'] = todays_active_user_count
        data['cumulative_active_user_count'] = get_previous_cumulative_active_user_count(
            date_for) + todays_active_user_count
        data['total_user_count'] = user_count
        data['course_count'] = course_count
        data['total_enrollment_count'] = get_total_enrollment_count(date_for)
        return data


class SiteDailyMetricsLoader(object):

    def __init__(self, extractor=None):
        self.extractor = extractor or SiteDailyMetricsExtractor()

    def load(self, date_for=None, force_update=False, **kwargs):
        '''
        TODO: Add filtering for
        * Multi-tenancy
        * Course acess groups
        '''
        if not date_for:
            date_for = prev_day(
                datetime.datetime.utcnow().replace(tzinfo=utc).date()
                )

        # if we already have a record for the date_for and force_update is False
        # then skip getting data
        if not force_update:
            try:
                sdm = SiteDailyMetrics.objects.get(date_for=date_for)
                return (sdm, False,)

            except SiteDailyMetrics.DoesNotExist:
                # proceed normally
                pass

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
        results = SiteDailyMetricsLoader().load(
            date_for=kwargs.get('date_for', None),
            force_update=kwargs.get('force_update'),
            )
        return results
