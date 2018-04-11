'''
Provides filtering for objects retrieved in edX Figures
'''

from django.contrib.auth import get_user_model
import django_filters

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)


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


class UserFilter(django_filters.FilterSet):
    '''Provides filtering for User model objects

    Note: User has a 1:1 relationship with the edx-platform LMS
    studen.models.UserProfile model

    We're starting with a few fields and will add as we find we want/need them

    '''
    is_active = django_filters.BooleanFilter(name='is_active',)
    username = django_filters.CharFilter(lookup_type='icontains')
    email = django_filters.CharFilter(lookup_type='icontains')
    country = django_filters.CharFilter(
        name='profile__country', lookup_type='iexact')

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'country', 'is_active', 'is_staff',
                  'is_superuser', ]
