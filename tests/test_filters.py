'''
Unit tests for the edx-figures filter classes
'''

import pytest

from django.test import TestCase

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from edx_figures.filters import (
    CourseOverviewFilter,
)

from .factories import CourseOverviewFactory
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
