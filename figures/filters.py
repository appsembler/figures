'''
Provides filtering for objects retrieved in Figures
'''

from django.contrib.auth import get_user_model
import django_filters

from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)
from student.models import CourseEnrollment

from figures.models import CourseDailyMetrics, SiteDailyMetrics


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

    display_name = django_filters.CharFilter(lookup_type='icontains')
    org = django_filters.CharFilter(
        name='display_org_with_default', lookup_type='iexact')
    number = django_filters.CharFilter(
        name='display_number_with_default', lookup_type='iexact')
    number_contains = django_filters.CharFilter(
        name='display_number_with_default', lookup_type='icontains')

    class Meta:
        model = CourseOverview
        fields = ['display_name', 'org', 'number', 'number_contains', ]


class CourseEnrollmentFilter(django_filters.FilterSet):
    '''Provides filtering for the CourseEnrollment model objects

    '''

    course_id = django_filters.MethodFilter(action='filter_course_id')
    is_active = django_filters.BooleanFilter(name='is_active',)

    def filter_course_id(self, queryset, course_id_str):
        '''

        This method converts the course id string to a CourseLocator object
        and returns the filtered queryset. This is required because
        CourseEnrollment course_id fields are of type CourseKeyField

        Query parameters with plus signs '+' in the string are automatically
        replaced with spaces, so we need to put the '+' back in for CourseKey
        to be able to create a course key object from the string
        '''
        course_key = CourseKey.from_string(course_id_str.replace(' ', '+'))
        return queryset.filter(course_id=course_key)

    class Meta:
        model = CourseEnrollment
        fields = ['course_id', 'user_id', 'is_active', ]


class UserFilterSet(django_filters.FilterSet):
    '''Provides filtering for User model objects

    Note: User has a 1:1 relationship with the edx-platform LMS
    student.models.UserProfile model

    We're starting with a few fields and will add as we find we want/need them

    '''
    is_active = django_filters.BooleanFilter(name='is_active',)
    username = django_filters.CharFilter(lookup_type='icontains')
    email = django_filters.CharFilter(lookup_type='icontains')
    country = django_filters.CharFilter(
        name='profile__country', lookup_type='iexact')

    user_ids = django_filters.MethodFilter(action='filter_user_ids')
    enrolled_in_course_id = django_filters.MethodFilter(
        action='filter_enrolled_in_course_id')

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'country', 'is_active', 'is_staff',
                  'is_superuser', 'enrolled_in_course_id', 'user_ids', ]

    def filter_user_ids(self, queryset, user_ids_str):

        user_ids = [id for id in user_ids_str.split(',') if id.isdigit()]
        return queryset.filter(id__in=user_ids)

    def filter_enrolled_in_course_id(self, queryset, course_id_str):
        '''

        This method converts the course id string to a CourseLocator object
        and returns the filtered queryset. This is required because
        CourseEnrollment course_id fields are of type CourseKeyField

        Query parameters with plus signs '+' in the string are automatically
        replaced with spaces, so we need to put the '+' back in for CourseKey
        to be able to create a course key object from the string
        '''
        course_key = CourseKey.from_string(course_id_str.replace(' ', '+'))
        # get course enrollments for the course
        user_ids = CourseEnrollment.objects.filter(
            course_id=course_key).values_list('user__id', flat=True).distinct()
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
