'''
Unit tests for the edx-figures filter classes
'''

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from edx_figures.filters import (
    CourseOverviewFilter,
    UserFilter,
)

from .factories import CourseOverviewFactory, UserFactory
from .helpers import make_course_key_str

# Because we are testing filtering on CourseOverviewFields, we want to set
# specific values to facilitate filtering
COURSE_DATA = [
    { 'org': 'AlphaOrg', 'number': 'A001' },
    { 'org': 'AlphaOrg', 'number': 'A002' },
    { 'org': 'BravoOrg', 'number': 'B001' },
    { 'org': 'BravoOrg', 'number': 'B002' },
]

def make_course(**kwargs):
    id = make_course_key_str(**kwargs)
    return CourseOverviewFactory(
        id=id, org=kwargs['org'], number=kwargs['number'])

USER_DATA = [
    { 'id': 1, 'username': u'alpha',   'fullname': u'Alpha One' },
    { 'id': 2, 'username': u'alpha02', 'fullname': u'Alpha Two' },
    { 'id': 3, 'username': u'bravo',   'fullname': u'Bravo One' },
    { 'id': 4, 'username': u'bravo02', 'fullname': u'Bravo Two' },
]

def make_user(**kwargs):
    return UserFactory(
        id=kwargs['id'], username=kwargs['username'], profile__name=kwargs['fullname'])


@pytest.mark.django_db
class CourseOverviewFilterTest(TestCase):
    def setUp(self):
        self.course_overviews = [make_course(**data) for data in COURSE_DATA]

    def tearDown(self):
        pass

    def test_get_all_courses(self):
        f = CourseOverviewFilter(queryset=CourseOverview.objects.all())
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.course_overviews],
            lambda o: o.id, 
            ordered=False)

    def test_filter_exact_org(self):
        f = CourseOverviewFilter(
            queryset=CourseOverview.objects.filter(org='Alpha'))
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.course_overviews if o.org=='Alpha'],
            lambda o: o.id, 
            ordered=False)

    def test_filter_exact_number(self):
        f = CourseOverviewFilter(
            queryset=CourseOverview.objects.filter(number='A001'))
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.course_overviews if o.number=='A001'],
            lambda o: o.id, 
            ordered=False)

    def test_filter_number_contains(self):
        f = CourseOverviewFilter(
            queryset=CourseOverview.objects.filter(number__contains='001'))
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.course_overviews if '001' in o.number],
            lambda o: o.id, 
            ordered=False)


@pytest.mark.django_db
class UserFilterTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.users = [make_user(**data) for data in USER_DATA]

    def tearDown(self):
        pass

    def test_get_all_users(self):
        f = UserFilter(queryset=self.User.objects.all())
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.users],
            lambda o: o.id, 
            ordered=False)

