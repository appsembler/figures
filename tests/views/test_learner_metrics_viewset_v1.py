"""Tests Figures learner-metrics viewset
"""

import pytest

import django.contrib.sites.shortcuts
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from figures.helpers import as_course_key
from figures.sites import (
    get_course_keys_for_site,
    users_enrolled_in_courses,
)
from figures.views import LearnerMetricsViewSetV1

from tests.helpers import organizations_support_sites
from tests.views.base import BaseViewTest
from tests.views.helpers import is_response_paginated, make_caller


def filter_enrollments(enrollments, courses):
    course_ids = [elem.id for elem in courses]
    return [elem for elem in enrollments if elem.course_id in course_ids]


@pytest.mark.django_db
class TestLearnerMetricsViewSetV1(BaseViewTest):
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
    base_request_path = 'api/learner-metrics-v1/'
    view_class = LearnerMetricsViewSetV1

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        if organizations_support_sites():
            settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        super(TestLearnerMetricsViewSetV1, self).setup(db)

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

    def matching_enrollment_set_to_course_ids(self, enrollments, course_ids):
        """
        enrollment course ids need to be a subset of course_ids
        It is ok if there are none or fewer enrollments than course_ids because
        a learner might not be enrolled in all the courses on which we are
        filtering
        """
        enroll_course_ids = set([rec['course_id'] for rec in enrollments])
        return enroll_course_ids.issubset(set([str(rec) for rec in course_ids]))

    def test_list_method_all(self, monkeypatch, lm_test_data):
        """Partial test coverage to check we get all site users

        Checks returned user ids against all user ids for the site
        Checks top level keys

        Does NOT check values in the `enrollments` key. This should be done as
        follow up work
        """
        us = lm_test_data['us']
        them = lm_test_data['them']
        our_courses = us['courses']
        caller = make_caller(us['org'])
        assert us['site'].domain != them['site'].domain
        assert len(our_courses) > 1

        response = self.make_request(request_path=self.base_request_path,
                                     monkeypatch=monkeypatch,
                                     site=us['site'],
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check users
        result_ids = [obj['id'] for obj in results]
        # Get all enrolled users
        course_keys = get_course_keys_for_site(site=us['site'])
        users = users_enrolled_in_courses(course_keys)
        user_ids = [user.id for user in users]
        assert set(result_ids) == set(user_ids)
        # Spot check the first record
        top_keys = ['id', 'username', 'email', 'fullname', 'is_active',
                    'date_joined', 'enrollments']
        assert set(results[0].keys()) == set(top_keys)

    def test_course_param_single(self, monkeypatch, lm_test_data):
        """Test that the 'course' query parameter works

        """
        us = lm_test_data['us']
        them = lm_test_data['them']
        our_enrollments = us['enrollments']
        our_courses = us['courses']

        caller = make_caller(us['org'])
        assert us['site'].domain != them['site'].domain
        assert len(our_courses) > 1
        query_params = '?course={}'.format(str(our_courses[0].id))

        request_path = self.base_request_path + query_params
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=us['site'],
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check user ids
        result_ids = [obj['id'] for obj in results]

        course_enrollments = [elem for elem in our_enrollments
                              if elem.course_id == our_courses[0].id]
        expected_user_ids = [obj.user.id for obj in course_enrollments]
        assert set(result_ids) == set(expected_user_ids)

        for rec in results:
            assert self.matching_enrollment_set_to_course_ids(
                rec['enrollments'], [our_courses[0].id])

    def test_course_param_multiple(self, monkeypatch, lm_test_data):
        """Test that the 'course' query parameter works

        """
        us = lm_test_data['us']
        them = lm_test_data['them']
        our_enrollments = us['enrollments']
        our_courses = us['courses']
        caller = make_caller(us['org'])
        assert us['site'].domain != them['site'].domain
        assert len(our_courses) > 1

        filtered_courses = our_courses[:2]

        # TODO: build params from 'filtered_courses'
        query_params = '?course={}&course={}'.format(str(our_courses[0].id),
                                                     str(our_courses[1].id))

        request_path = self.base_request_path + query_params
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=us['site'],
                                     caller=caller,
                                     action='list')

        # Continue updating here
        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check user ids
        result_ids = [obj['id'] for obj in results]
        expected_enrollments = filter_enrollments(enrollments=our_enrollments,
                                                  courses=filtered_courses)
        expected_user_ids = [obj.user.id for obj in expected_enrollments]
        assert set(result_ids) == set(expected_user_ids)
        for rec in results:
            assert self.matching_enrollment_set_to_course_ids(
                rec['enrollments'], [rec.id for rec in filtered_courses])

    @pytest.mark.parametrize('query_param, field_name', [
        ('username', 'username'),
        ('email', 'email'),
        ])
    def test_distinct_user(self, monkeypatch, lm_test_data, query_param, field_name):
        """

        Test data setup:
        We need to have a user enrolled in multiple courses

        We expect to have just one user record returned with each of the
        courses for which the user is enrolled
        """
        # Set up data
        us = lm_test_data['us']
        our_enrollments = us['enrollments']
        caller = make_caller(us['org'])
        our_site_users = lm_test_data['us']['users']
        our_user = our_site_users[-1]
        user_ce = [rec for rec in our_enrollments if rec.user_id == our_user.id]
        query_val = getattr(our_user, field_name)
        query_str = '?{}={}'.format(query_param, query_val)

        # Run test
        request_path = self.base_request_path + query_str
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=us['site'],
                                     caller=caller,
                                     action='list')
        # Check results
        # Continue updating here
        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        found_ce_ids = set([rec['id'] for rec in results[0]['enrollments']])
        assert len(results) == 1
        assert results[0]['id'] == our_user.id
        assert found_ce_ids == set([rec.id for rec in user_ce])

    def invalid_course_ids_raise_404(self, monkeypatch, lm_test_data, query_params):
        """
        Helper method to test expected 404 calls
        """
        us = lm_test_data['us']
        them = lm_test_data['them']

        caller = make_caller(us['org'])
        assert us['site'].domain != them['site'].domain
        request_path = self.base_request_path + query_params
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=us['site'],
                                     caller=caller,
                                     action='list')
        return response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.skipif(not organizations_support_sites(),
                        reason='Organizations support sites')
    def test_valid_and_course_param_from_other_site_invalid(self,
                                                            monkeypatch,
                                                            lm_test_data):
        """Test that the 'course' query parameter works

        """
        our_courses = lm_test_data['us']['courses']
        their_courses = lm_test_data['them']['courses']
        query_params = '?course={}&course={}'.format(str(our_courses[0].id),
                                                     str(their_courses[0].id))
        assert self.invalid_course_ids_raise_404(monkeypatch,
                                                 lm_test_data,
                                                 query_params)

    def test_valid_and_mangled_course_param_invalid(self,
                                                    monkeypatch,
                                                    lm_test_data):
        """Test that the 'course' query parameter works

        """
        our_courses = lm_test_data['us']['courses']
        mangled_course_id = 'she-sell-seashells-by-the-seashore'
        query_params = '?course={}&course={}'.format(str(our_courses[0].id),
                                                     mangled_course_id)
        assert self.invalid_course_ids_raise_404(monkeypatch,
                                                 lm_test_data,
                                                 query_params)

    def test_unlinked_course_id_param_invalid(self, monkeypatch, lm_test_data):
        """Test that the 'course' query parameter works

        """
        our_courses = lm_test_data['us']['courses']
        unlinked_course_id = as_course_key('course-v1:UnlinkedCourse+UMK+1999')
        query_params = '?course={}&course={}'.format(str(our_courses[0].id),
                                                     unlinked_course_id)
        assert self.invalid_course_ids_raise_404(monkeypatch,
                                                 lm_test_data,
                                                 query_params)
