"""Tests Figures learner-metrics viewset
"""

import pytest

import django.contrib.sites.shortcuts
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from figures.sites import get_user_ids_for_site
from figures.views import LearnerMetricsViewSet

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    # LearnerCourseGradeMetricsFactory,
    OrganizationFactory,
    SiteFactory,
    UserFactory,
)

from tests.helpers import organizations_support_sites
from tests.views.base import BaseViewTest
from tests.views.helpers import is_response_paginated

if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory

    def map_users_to_org_site(caller, site, users):
        org = OrganizationFactory(sites=[site])
        UserOrganizationMappingFactory(user=caller,
                                       organization=org,
                                       is_amc_admin=True)
        [UserOrganizationMappingFactory(user=user,
                                        organization=org) for user in users]
        # return created objects that the test will need
        return caller


@pytest.fixture
def enrollment_test_data():
    """Stands up shared test data. We need to revisit this
    """
    num_courses = 2
    site = SiteFactory()
    course_overviews = [CourseOverviewFactory() for i in range(num_courses)]
    # Create a number of enrollments for each course
    enrollments = []
    for num_enroll, co in enumerate(course_overviews, 1):
        enrollments += [CourseEnrollmentFactory(
            course_id=co.id) for i in range(num_enroll)]

    # This is a convenience for the test method
    users = [enrollment.user for enrollment in enrollments]
    return dict(
        site=site,
        course_overviews=course_overviews,
        enrollments=enrollments,
        users=users,
    )


@pytest.mark.django_db
class TestLearnerMetricsViewSet(BaseViewTest):
    """Tests the learner metrics viewset

    The tests are incomplete

    The list action will return a list of the following records:

    ```
        {
            "id": 109,
            "username": "chasecynthia",
            "email": "msnyder@gmail.com",
            "fullname": "Brandon Meyers",
            "is_active": true,
            "date_joined": "2020-06-03T00:00:00Z",
            "enrollments": [
                {
                    "id": 9,
                    "course_id": "course-v1:StarFleetAcademy+SFA01+2161",
                    "date_enrolled": "2020-02-24",
                    "is_enrolled": true,
                    "progress_percent": 1.0,
                    "progress_details": {
                        "sections_worked": 20,
                        "points_possible": 100.0,
                        "sections_possible": 20,
                        "points_earned": 50.0
                    }
                }
            ]
        }
    ```
    """
    base_request_path = 'api/learner-metrics/'
    view_class = LearnerMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        if organizations_support_sites():
            settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        super(TestLearnerMetricsViewSet, self).setup(db)

    def make_caller(self, site, users):
        """Convenience method to create the API caller user
        """
        if organizations_support_sites():
            # TODO: set is_staff to False after we have test coverage
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=users)
        else:
            caller = UserFactory(is_staff=True)
        return caller

    def make_request(self, monkeypatch, request_path, site, caller, action):
        """Convenience method to make the API request

        Returns the response object
        """
        request = APIRequestFactory().get(request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': action})
        return view(request)

    def test_list_method_all(self, monkeypatch, enrollment_test_data):
        """Partial test coverage to check we get all site users

        Checks returned user ids against all user ids for the site
        Checks top level keys

        Does NOT check values in the `enrollments` key. This should be done as
        follow up work
        """
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']

        caller = self.make_caller(site, users)
        other_site = SiteFactory()
        assert site.domain != other_site.domain

        response = self.make_request(request_path=self.base_request_path,
                                     monkeypatch=monkeypatch,
                                     site=site,
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check user ids
        result_ids = [obj['id'] for obj in results]
        user_ids = get_user_ids_for_site(site=site)
        assert set(result_ids) == set(user_ids)
        # Spot check the first record
        top_keys = ['id', 'username', 'email', 'fullname', 'is_active',
                    'date_joined', 'enrollments']
        assert set(results[0].keys()) == set(top_keys)

    def test_course_param_single(self, monkeypatch, enrollment_test_data):
        """Test that the 'course' query parameter works

        """
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']
        enrollments = enrollment_test_data['enrollments']
        course_overviews = enrollment_test_data['course_overviews']

        caller = self.make_caller(site, users)
        other_site = SiteFactory()
        assert site.domain != other_site.domain
        assert len(course_overviews) > 1
        query_params = '?course={}'.format(str(course_overviews[0].id))

        request_path = self.base_request_path + query_params
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=site,
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check user ids
        result_ids = [obj['id'] for obj in results]

        our_enrollments = [elem for elem in enrollments if elem.course_id == course_overviews[0].id]
        expected_user_ids = [obj.user.id for obj in our_enrollments]
        assert set(result_ids) == set(expected_user_ids)

    def test_course_param_multiple(self, monkeypatch, enrollment_test_data):
        """Test that the 'course' query parameter works

        """
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']
        enrollments = enrollment_test_data['enrollments']
        course_overviews = enrollment_test_data['course_overviews']

        caller = self.make_caller(site, users)
        other_site = SiteFactory()
        assert site.domain != other_site.domain
        assert len(course_overviews) > 1
        query_params = '?course={}&course={}'.format(str(course_overviews[0].id),
                                                     str(course_overviews[1].id))

        request_path = self.base_request_path + query_params
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=site,
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check user ids
        result_ids = [obj['id'] for obj in results]
        expected_user_ids = [obj.user.id for obj in enrollments]
        assert set(result_ids) == set(expected_user_ids)
