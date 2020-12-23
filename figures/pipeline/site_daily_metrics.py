"""This module populates the figures.models.SiteDailyMetrics model


Most of the data are from CourseDailyMetrics. Some data are not captured in
course metrics. These data are extracted directly from edx-platform models

"""

from __future__ import absolute_import

from django.db.models import Sum

from figures.helpers import as_course_key, as_datetime, next_day
from figures.mau import site_mau_1g_for_month_as_of_day
from figures.models import CourseDailyMetrics, SiteDailyMetrics
from figures.sites import (
    get_courses_for_site,
    get_users_for_site,
    get_student_modules_for_site,
)
from figures.pipeline.helpers import pipeline_date_for_rule


#
# Standalone helper methods
#


def missing_course_daily_metrics(site, date_for):
    '''
    Return a list of course ids for any courses missing from the set of
    CourseDailyMetrics for the given date (and site after we implement multi-
    tenancy)

    The type returned is CourseLocator

    We use this to make sure that we are not missing course data when we
    populat the SiteDailyMetrics instance for the given date

    '''
    cdm_course_keys = [
        as_course_key(cdm.course_id) for cdm in
        CourseDailyMetrics.objects.filter(site=site, date_for=date_for)
    ]

    site_course_overviews = get_courses_for_site(site)
    course_overviews = site_course_overviews.filter(
        created__lt=as_datetime(next_day(date_for))).exclude(id__in=cdm_course_keys)

    return set(course_overviews.values_list('id', flat=True))


#
# Standalone methods to extract data/aggregate data for use in SiteDailyMetrics
#

def get_site_active_users_for_date(site, date_for):
    '''
    Get the active users ids for the given site and date

    We do this by filtering StudentModule for courses in the site, then
    for StudentModule records filtered for the date, then we get the distinct
    user ids
    '''
    student_modules = get_student_modules_for_site(site)

    # For Ginkgo backward compatibility, Django 1.8 does not support
    # `modified__date=<some_value>` in filters. Therefore, we need to match
    # each date field
    return student_modules.filter(modified__year=date_for.year,
                                  modified__month=date_for.month,
                                  modified__day=date_for.day).values_list(
        'student__id', flat=True).distinct()


def get_previous_cumulative_active_user_count(site, date_for):
    ''' Returns the previous cumulative site-wide active user count

    It finds the most recent record before `date_for`. If a record is found,
    returns the `cumulative_active_user_count` of that records.

    Returns 0 if there is no record for the previous day
    '''
    rec = SiteDailyMetrics.latest_previous_record(site=site, date_for=date_for)
    if rec:
        return rec.cumulative_active_user_count or 0
    else:
        return 0


def get_total_enrollment_count(site, date_for, course_ids=None):  # pylint: disable=unused-argument
    '''Returns the total enrollments across all courses for the site
    It does not return unique learners
    '''
    aggregates = CourseDailyMetrics.objects.filter(
        site=site, date_for=date_for).aggregate(
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

    def extract(self, site, date_for, **kwargs):  # pylint: disable=unused-argument
        '''
        We get the count from the User model since there can be registered users
        who have not enrolled.

        TODO: Exclude non-students from the user count
        '''
        data = dict()

        site_users = get_users_for_site(site)
        user_count = site_users.filter(
            date_joined__lt=as_datetime(next_day(date_for))).count()
        site_courses = get_courses_for_site(site)
        course_count = site_courses.filter(
            created__lt=as_datetime(next_day(date_for))).count()

        todays_active_users = get_site_active_users_for_date(site, date_for)
        todays_active_user_count = todays_active_users.count()
        mau = site_mau_1g_for_month_as_of_day(site, date_for)

        data['todays_active_user_count'] = todays_active_user_count
        data['cumulative_active_user_count'] = get_previous_cumulative_active_user_count(
            site, date_for) + todays_active_user_count
        data['total_user_count'] = user_count
        data['course_count'] = course_count
        data['total_enrollment_count'] = get_total_enrollment_count(site, date_for)
        data['mau'] = mau.count()
        return data


class SiteDailyMetricsLoader(object):

    def __init__(self, extractor=None):
        self.extractor = extractor or SiteDailyMetricsExtractor()

    def load(self, site, date_for=None, force_update=False, **_kwargs):
        """
        Architectural note:
        Initially, we're going to be explicit, requiring callers to specify the
        site model instance to be associated with the site specific metrics
        model(s) we are populating

        TODOs:
        Add filtering for
        * Multi-tenancy
        * Course acess groups
        """
        date_for = pipeline_date_for_rule(date_for)

        # if we already have a record for the date_for and force_update is False
        # then skip getting data
        if not force_update:
            try:
                sdm = SiteDailyMetrics.objects.get(site=site, date_for=date_for)
                return (sdm, False,)

            except SiteDailyMetrics.DoesNotExist:
                # proceed normally
                pass

        data = self.extractor.extract(site=site, date_for=date_for)
        site_metrics, created = SiteDailyMetrics.objects.update_or_create(
            date_for=date_for,
            site=site,
            defaults=dict(
                cumulative_active_user_count=data['cumulative_active_user_count'],
                todays_active_user_count=data['todays_active_user_count'],
                total_user_count=data['total_user_count'],
                course_count=data['course_count'],
                total_enrollment_count=data['total_enrollment_count'],
                mau=data['mau'],
            )
        )
        return site_metrics, created
