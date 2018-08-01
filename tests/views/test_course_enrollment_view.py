'''Unit tests for the course enrollment view
'''

import datetime
from dateutil.parser import parse
import pytest

from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from opaque_keys.edx.keys import CourseKey

from student.models import CourseEnrollment

from figures.views import CourseEnrollmentViewSet

from tests.factories import(
    COURSE_ID_STR_TEMPLATE,
    CourseEnrollmentFactory,
    UserFactory,
)


def sample_course_id(index=1):
    return CourseKey.from_string(COURSE_ID_STR_TEMPLATE.format(index))


@pytest.mark.django_db
class TestCourseEnrollment(object):
    '''
        TODO: Add test for course_id. Issue with 

    Have this to address:
        "course-v1:Appsembler EdX101 2015_Spring" is not an instance of 
        <class 'opaque_keys.edx.keys.CourseKey'>

    An issue is that the mocks user strings for course_id fields instead of CourseKey
    
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.special_fields = ('create', 'user',)
        self.course_enrollments = [
            CourseEnrollmentFactory() for i in range(1,5)
        ]

        self.sample_course_id = self.course_enrollments[0].course_id

    @pytest.mark.parametrize('endpoint, filter_args', [
            ('api/course-enrollments/', {}),
            ('api/course-enrollments/?course_id={}'.format(
                str(sample_course_id(1))), 
            { 'course_id': sample_course_id(1)}),
        ])
    def test_get_course_enrollments(self, endpoint, filter_args):
        expected_data = CourseEnrollment.objects.filter(**filter_args)

        factory = APIRequestFactory()
        request = factory.get(endpoint)
        force_authenticate(request, user=UserFactory())
        view = CourseEnrollmentViewSet.as_view({'get': 'list'})
        response = view(request)

        assert response.status_code == 200
        assert set(response.data.keys()) == set(
            ['count', 'next', 'previous', 'results',])

        assert len(response.data['results']) == len(expected_data)

        for data in response.data['results']:
            db_rec = expected_data.get(id=data['id'])
            assert parse(data['created']) == db_rec.created

