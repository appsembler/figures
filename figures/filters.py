"""Provides filtering for objects retrieved in Figures

*IMPORTANT: The Hawthorn upgrade currently breaks use of Django Filter versions prior to 1.0

This means filters are not compatible with releases prior to Hawthorn.

Some work has been done to support Django Filter prior to 1.0 but it is not complete.

See the following for breaking changes when upgrading to Django Filter 1.0:

https://django-filter.readthedocs.io/en/master/guide/migration.html#migrating-to-1-0

TODO: Rename classes so they eiher all end with "Filter" or "FilterSet" then
      update the test class names in "tests/test_filters.py" to match.
"""

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db.models import F

import django_filters

from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview  # noqa pylint: disable=import-error

from student.models import CourseEnrollment  # pylint: disable=import-error

from figures.pipeline.course_daily_metrics import get_enrolled_in_exclude_admins
from figures.models import (
    CourseDailyMetrics,
    SiteDailyMetrics,
    CourseMauMetrics,
    LearnerCourseGradeMetrics,
    SiteMauMetrics,
)


def char_method_filter(method):
    """
    "method" is the method name string
    First check for old style (pre  version 1 Django Filters)
    """
    if hasattr(django_filters, 'MethodFilter'):
        return django_filters.MethodFilter(action=method)  # pylint: disable=no-member
    else:
        return django_filters.CharFilter(method=method)


def boolean_method_filter(method):
    """
    "method" is the method name string
    First check for old style (pre version 1 Django Filters)
    """
    if hasattr(django_filters, 'MethodFilter'):
        return django_filters.MethodFilter(action=method)  # pylint: disable=no-member
    else:
        return django_filters.BooleanFilter(method=method)


class CourseOverviewFilter(django_filters.FilterSet):
    '''Provides filtering for CourseOverview model objects

    Filters to consider adding:
        description: search/icontains
        enrollment start: date exact/lt, gt, range
        enrollment end: date exact/lt, gt, range

    Outstanding issues:

        CourseOverview.id is not yet in the filter, as filtering a
        string representation of the course id in the query params
        causes the following::

            AssertionError: <course id string repr> is not an instance of
            <class 'opaque_keys.edx.keys.CourseKey'>

    '''

    display_name = django_filters.CharFilter(lookup_expr='icontains')
    org = django_filters.CharFilter(
        name='display_org_with_default', lookup_expr='iexact')
    number = django_filters.CharFilter(
        name='display_number_with_default', lookup_expr='iexact')
    number_contains = django_filters.CharFilter(
        name='display_number_with_default', lookup_expr='icontains')

    class Meta:
        model = CourseOverview
        fields = ['display_name', 'org', 'number', 'number_contains', ]


class CourseEnrollmentFilter(django_filters.FilterSet):
    '''Provides filtering for the CourseEnrollment model objects

    '''
    course_id = char_method_filter(method='filter_course_id')
    is_active = django_filters.BooleanFilter(name='is_active',)

    def filter_course_id(self, queryset, name, value):  # pylint: disable=unused-argument
        '''

        This method converts the course id string to a CourseLocator object
        and returns the filtered queryset. This is required because
        CourseEnrollment course_id fields are of type CourseKeyField

        Query parameters with plus signs '+' in the string are automatically
        replaced with spaces, so we need to put the '+' back in for CourseKey
        to be able to create a course key object from the string
        '''
        course_key = CourseKey.from_string(value.replace(' ', '+'))
        return queryset.filter(course_id=course_key)

    class Meta:
        model = CourseEnrollment
        fields = ['course_id', 'user_id', 'is_active', ]


class EnrollmentMetricsFilter(CourseEnrollmentFilter):
    """Filter query params for enrollment metrics

    Consider making 'user_ids' and 'course_ids' be mixins for `user` foreign key
    and 'course_id' respectively. Perhaps a class decorator if there's some
    unforseen issue with doing a mixin for each

    Filters

    "course_ids" filters on a set of comma delimited course id strings
    "user_ids" filters on a set of comma delimited integer user ids
    "only_completed" shows only completed records. Django Filter 1.0.4 appears
    to only support capitalized "True" as the value in the query string

    The "only_completed" filter is subject to change. We want to be able to
    filter on: "hide completed", "show only completed", "show everything"
    So we may go with a "choice field"

    Use ``date_for`` for retrieving a specific date
    Use ``date_0`` and ``date_1`` for retrieving values in a date range, inclusive
    each of these can be used singly to get:
    * ``date_0`` to get records greater than or equal
    * ``date_1`` to get records less than or equal

    TODO: Add 'is_active' filter - need to find matches in CourseEnrollment
    """
    course_ids = char_method_filter(method='filter_course_ids')
    user_ids = char_method_filter(method='filter_user_ids')
    date = django_filters.DateFromToRangeFilter(name='date_for')
    only_completed = boolean_method_filter(method='filter_only_completed')
    exclude_completed = boolean_method_filter(method='filter_exclude_completed')

    class Meta:
        """
        Allow all field and related filtering except for "site"
        """
        model = LearnerCourseGradeMetrics
        exclude = ['site']

    def filter_course_ids(self, queryset, name, value):  # pylint: disable=unused-argument
        course_ids = [cid.replace(' ', '+') for cid in value.split(',')]
        return queryset.filter(course_id__in=course_ids)

    def filter_user_ids(self, queryset, name, value):  # pylint: disable=unused-argument
        """
        """
        user_ids = [user_id for user_id in value.split(',') if user_id.isdigit()]
        return queryset.filter(user_id__in=user_ids)

    def filter_only_completed(self, queryset, name, value):  # pylint: disable=unused-argument
        """
        The "value" parameter is either `True` or `False`
        """
        if value is True:
            return queryset.filter(sections_possible__gt=0,
                                   sections_worked=F('sections_possible'))
        else:
            return queryset

    def filter_exclude_completed(self, queryset, name, value):  # pylint: disable=unused-argument
        """
        The "value" parameter is either `True` or `False`
        """
        if value is True:
            # This is a hack until we add `completed` field to LCGM
            return queryset.filter(sections_worked__lt=F('sections_possible'))
        else:
            return queryset


class UserFilterSet(django_filters.FilterSet):
    '''Provides filtering for User model objects

    Note: User has a 1:1 relationship with the edx-platform LMS
    student.models.UserProfile model

    We're starting with a few fields and will add as we find we want/need them

    '''
    is_active = django_filters.BooleanFilter(name='is_active')
    is_staff = django_filters.BooleanFilter(name='is_staff')
    is_superuser = django_filters.BooleanFilter(name='is_superuser')
    username = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains', name='profile__name')

    country = django_filters.CharFilter(
        name='profile__country', lookup_expr='iexact')
    user_ids = char_method_filter(method='filter_user_ids')
    enrolled_in_course_id = char_method_filter(method='filter_enrolled_in_course_id')

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'name', 'country', 'is_active',
                  'is_staff', 'is_superuser', 'enrolled_in_course_id',
                  'user_ids', 'date_joined']

    def filter_user_ids(self, queryset, name, value):  # pylint: disable=unused-argument
        user_ids = [user_id for user_id in value.split(',') if user_id.isdigit()]
        return queryset.filter(id__in=user_ids)

    def filter_enrolled_in_course_id(self, queryset,
                                     name, value):  # pylint: disable=unused-argument
        '''

        This method converts the course id string to a CourseLocator object
        and returns the filtered queryset. This is required because
        CourseEnrollment course_id fields are of type CourseKeyField

        Query parameters with plus signs '+' in the string are automatically
        replaced with spaces, so we need to put the '+' back in for CourseKey
        to be able to create a course key object from the string
        '''
        course_key = CourseKey.from_string(value.replace(' ', '+'))
        enrollments = get_enrolled_in_exclude_admins(course_id=course_key)
        user_ids = enrollments.values_list('user__id', flat=True)
        return queryset.filter(id__in=user_ids)


class CourseDailyMetricsFilter(django_filters.FilterSet):
    '''Provides filtering for the courseDailyMetrics model objects

    This is a work in progress. Parameters need improvement, but have to dive
    into Django Filter more

    Use ``date_for`` for retrieving a specific date
    Use ``date_0`` and ``date_1`` for retrieving values in a date range, inclusive
    each of these can be used singly to get:
    * ``date_0`` to get records greater than or equal
    * ``date_1`` to get records less than or equal
    '''
    date = django_filters.DateFromToRangeFilter(name='date_for')

    class Meta:
        model = CourseDailyMetrics
        fields = ['date_for', 'date', 'course_id', ]


class SiteDailyMetricsFilter(django_filters.FilterSet):
    '''Provides filtering for the SiteDailyMetrics model objects

    This is a work in progress. Parameters need improvement, but have to dive
    into Django Filter more

    Use ``date_for`` for retrieving a specific date
    Use ``date_0`` and ``date_1`` for retrieving values in a date range, inclusive
    each of these can be used singly to get:
    * ``date_0`` to get records greater than or equal
    * ``date_1`` to get records less than or equal
    '''
    date = django_filters.DateFromToRangeFilter(name='date_for')

    class Meta:
        model = SiteDailyMetrics
        fields = ['date_for', 'date']


class CourseMauMetricsFilter(django_filters.FilterSet):
    """Provides filtering for CourseMauMetrics model objects


    Use ``date_for`` to retrieve a specific date
    Use ``date_0`` and ``date_1`` for retrieving values in a date range, inclusive
    each of these can be used singly to get:
    * ``date_0`` to get records greater than or equal
    * ``date_1`` to get records less than or equal
    """
    date = django_filters.DateFromToRangeFilter(name='date_for')

    class Meta:
        model = CourseMauMetrics
        fields = ['date_for', 'date', 'course_id', ]


class SiteMauMetricsFilter(django_filters.FilterSet):
    """Provides filtering for SiteDailyMetrics model objects

    Use ``date_for`` for retrieving a specific date
    Use ``date_0`` and ``date_1`` for retrieving values in a date range, inclusive
    each of these can be used singly to get:
    * ``date_0`` to get records greater than or equal
    * ``date_1`` to get records less than or equal
    """
    date = django_filters.DateFromToRangeFilter(name='date_for')

    class Meta:
        model = SiteMauMetrics
        fields = ['date_for', 'date']


class SiteFilterSet(django_filters.FilterSet):
    """
    Note: The Site filter has no knowledge of a default site, nor should it
    """
    domain = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Site
        fields = ['domain', 'name']
