'''
Test the views in edX Figures
'''

import pytest
from django.test import TestCase
from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older rest_framework versions
    force_authenticate,
    )

from edx_figures.views import (
    CoursesIndexView,
    )

from .factories import CourseOverviewFactory

# Course data and generate method are duplicates course data in test_filters.py
COURSE_DATA = [
    { 'id': u'course-v1:AlphaOrg+A001+RUN', 'name': u'Alpha Course 1', 'org': u'AlphaOrg', 'number': u'A001' },
    { 'id': u'course-v1:AlphaOrg+A002+RUN', 'name': u'Alpha Course 2', 'org': u'AlphaOrg', 'number': u'A002' },
    { 'id': u'course-v1:BravoOrg+A001+RUN', 'name': u'Bravo Course 1', 'org': u'BravoOrg', 'number': u'B001' },
    { 'id': u'course-v1:BravoOrg+B002+RUN', 'name': u'Bravo Course 2', 'org': u'BravoOrg', 'number': u'B002' },
]


# Look into renaming 'name' to 'display_name'
def make_course(**kwargs):
    return CourseOverviewFactory(
        id=kwargs['id'], display_name=kwargs['name'], org=kwargs['org'], number=kwargs['number'])


class CourseIndexViewTest(TestCase):
    def setUp(self):
        self.course_overviews = [make_course(**data) for data in COURSE_DATA]

    def tearDown(self):
        pass

    def test_get_all(self):
        expected_data = COURSE_DATA

        factory = APIRequestFactory()
        request = factory.get('api/courses-index/')
        view = CoursesIndexView.as_view()
        response = view(request)
        assert response.status_code == 200
        assert response.data == expected_data

    def test_get_org_filtered(self):
        expected_data = [rec for rec in COURSE_DATA if rec['org'] == 'AlphaOrg']

        factory = APIRequestFactory()
        request = factory.get('api/courses-index/?org=AlphaOrg')
        view = CoursesIndexView.as_view()
        response = view(request)
        assert response.status_code == 200
        assert response.data == expected_data

