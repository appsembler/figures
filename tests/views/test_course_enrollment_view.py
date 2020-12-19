"""Unit tests for the course enrollment view
"""

from __future__ import absolute_import

from dateutil.parser import parse
import pytest

from rest_framework.test import (
    APIRequestFactory,
    # RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from opaque_keys.edx.keys import CourseKey

from figures.compat import CourseEnrollment
from figures.helpers import is_multisite
from figures.views import CourseEnrollmentViewSet

from tests.factories import (
    COURSE_ID_STR_TEMPLATE,
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
)
from tests.helpers import organizations_support_sites
from tests.views.base import BaseViewTest
from six.moves import range

if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory


def sample_course_id(index=1):
    return CourseKey.from_string(COURSE_ID_STR_TEMPLATE.format(index))


@pytest.mark.django_db
class TestCourseEnrollmentViewSet(BaseViewTest):
    '''
        TODO: Add test for course_id. Issue with

    Have this to address:
        "course-v1:Appsembler EdX101 2015_Spring" is not an instance of
        <class 'opaque_keys.edx.keys.CourseKey'>

    An issue is that the mocks user strings for course_id fields instead of CourseKey

    '''

    request_path = 'api/course-enrollments/'
    view_class = CourseEnrollmentViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db):
        super(TestCourseEnrollmentViewSet, self).setup(db)
        self.special_fields = ('create', 'user',)
        self.course_overview = CourseOverviewFactory()
        self.course_enrollments = [
            CourseEnrollmentFactory(
                course_id=self.course_overview.id) for i in range(1, 5)
        ]

        self.sample_course_id = self.course_enrollments[0].course_id

        if is_multisite():
            self.organization = OrganizationFactory(sites=[self.site])
            OrganizationCourseFactory(organization=self.organization,
                                      course_id=str(self.course_overview.id))
            for ce in self.course_enrollments:
                UserOrganizationMappingFactory(user=ce.user, organization=self.organization)

    @pytest.mark.parametrize('query_params, filter_args', [
            ('', {}),
            ('?course_id={}'.format(str(sample_course_id(1))),
                {'course_id': sample_course_id(1)}),
    ])
    def test_get_course_enrollments(self, query_params, filter_args):
        expected_data = CourseEnrollment.objects.filter(**filter_args)
        request = APIRequestFactory().get(self.request_path + query_params)
        force_authenticate(request, user=self.staff_user)
        view = self. view_class.as_view({'get': 'list'})
        response = view(request)

        assert response.status_code == 200
        assert set(response.data.keys()) == set(
            ['count', 'next', 'previous', 'results'])

        assert len(response.data['results']) == len(expected_data)

        for data in response.data['results']:
            db_rec = expected_data.get(id=data['id'])
            assert parse(data['created']) == db_rec.created
