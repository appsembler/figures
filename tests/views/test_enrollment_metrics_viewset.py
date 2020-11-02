"""Tests Figures enrollment dta viewset
"""

from __future__ import absolute_import
from decimal import Decimal
import mock
import pytest

import django.contrib.sites.shortcuts
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from figures.models import LearnerCourseGradeMetrics
from figures.views import EnrollmentMetricsViewSet

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    LearnerCourseGradeMetricsFactory,
    OrganizationFactory,
    # OrganizationCourseFactory,
    SiteFactory,
    UserFactory,
)
from tests.helpers import organizations_support_sites
from tests.views.base import BaseViewTest
from tests.views.helpers import is_response_paginated
from six.moves import map
from six.moves import range

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
class TestEnrollmentMetricsViewSet(BaseViewTest):
    """
    Tests EnrollmentMetricsViewSet and EnrollmentMetricsFilter

    This is a quick "throw it together" test class. So there's significant room
    for improvement

    In order to get test coverage to pass, there are a few tests here.
    The ones testing query params should be able to be collapsed to a single
    parametrized test per endpoint, if we restructure and generalize the test
    data to have one set of test data serve mulitple conditions.

    TODO: Test main list method with the matrix of filter options
    - course_ids, user_ids,
    - Above mix with only_completed and with exclude_completed

    One option is to break this into different test classes, one for each action
    """
    base_request_path = 'api/enrollment-metrics/'
    view_class = EnrollmentMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        if organizations_support_sites():
            settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        super(TestEnrollmentMetricsViewSet, self).setup(db)

    def check_serialized_data(self, result_rec, obj):
        fields = ['id', 'course_id', 'date_for', 'points_earned',
                  'points_possible', 'sections_worked',
                  'sections_possible']
        expected_keys = fields + ['user', 'completed', 'progress_percent']
        assert set(result_rec.keys()) == set(expected_keys)

        for key in fields:
            obj_val = obj.__dict__[key]
            if key == 'date_for':
                obj_val = str(obj_val)
            assert result_rec[key] == obj_val
        assert result_rec['completed'] == obj.completed
        prog_pct = str(Decimal(obj.progress_percent).quantize(Decimal('.00')))
        assert result_rec['progress_percent'] == prog_pct

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
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']

        caller = self.make_caller(site, users)
        other_site = SiteFactory()
        assert site.domain != other_site.domain
        LearnerCourseGradeMetricsFactory(site=other_site)
        lcgm = [LearnerCourseGradeMetricsFactory(site=site) for i in range(5)]

        response = self.make_request(request_path=self.base_request_path,
                                     monkeypatch=monkeypatch,
                                     site=site,
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check keys
        result_ids = [obj['id'] for obj in results]
        assert set(result_ids) == set([obj.id for obj in lcgm])
        # Spot check the first record
        obj = LearnerCourseGradeMetrics.objects.get(id=results[0]['id'])
        self.check_serialized_data(results[0], obj)

    def test_list_method_filter_method_course_ids(self, monkeypatch, enrollment_test_data):
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']

        caller = self.make_caller(site, users)
        other_site = SiteFactory()
        assert site.domain != other_site.domain
        LearnerCourseGradeMetricsFactory(site=other_site)
        co = CourseOverviewFactory()
        LearnerCourseGradeMetricsFactory(site=site)

        co_lcgm = [LearnerCourseGradeMetricsFactory(
            site=site,
            course_id=str(co.id)) for i in range(5)]
        request_path = self.base_request_path + '?course_ids=' + str(co.id)
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=site,
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check keys
        result_ids = [obj['id'] for obj in results]
        assert set(result_ids) == set([obj.id for obj in co_lcgm])
        # Spot check the first record
        obj = LearnerCourseGradeMetrics.objects.get(id=results[0]['id'])
        self.check_serialized_data(results[0], obj)

    def test_list_method_filter_method_user_ids(self, monkeypatch, enrollment_test_data):
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']

        caller = self.make_caller(site, users)
        other_site = SiteFactory()
        assert site.domain != other_site.domain
        check_user = users[0]
        LearnerCourseGradeMetricsFactory(site=other_site)
        LearnerCourseGradeMetricsFactory(site=site)
        # Make sure we show only for our site for the selected user
        LearnerCourseGradeMetricsFactory(site=other_site, user=check_user)
        user_lcgm = [LearnerCourseGradeMetricsFactory(
            site=site, user=check_user) for i in range(3)]
        request_path = self.base_request_path + '?user_ids=' + str(check_user.id)
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=site,
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check keys
        result_ids = [obj['id'] for obj in results]
        assert set(result_ids) == set([obj.id for obj in user_lcgm])
        # Spot check the first record
        obj = LearnerCourseGradeMetrics.objects.get(id=results[0]['id'])
        self.check_serialized_data(results[0], obj)

    def test_list_method_filter_method_only_completed(self, monkeypatch, enrollment_test_data):
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']

        caller = self.make_caller(site, users)
        other_site = SiteFactory()
        assert site.domain != other_site.domain

        # Same test as for "test_completed_method"
        LearnerCourseGradeMetricsFactory(site=other_site,
                                         sections_worked=1,
                                         sections_possible=1)
        LearnerCourseGradeMetricsFactory(site=site,
                                         sections_worked=1,
                                         sections_possible=5)
        completed_lcgm = [LearnerCourseGradeMetricsFactory(site=site,
                                                           sections_worked=5,
                                                           sections_possible=5)
                          for i in range(3)]

        request_path = self.base_request_path + '?only_completed=True'
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=site,
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check keys
        result_ids = [obj['id'] for obj in results]
        assert set(result_ids) == set([obj.id for obj in completed_lcgm])
        # Spot check the first record
        obj = LearnerCourseGradeMetrics.objects.get(id=results[0]['id'])
        self.check_serialized_data(results[0], obj)

    def test_list_method_filter_method_exclude_completed(self, monkeypatch, enrollment_test_data):
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']

        caller = self.make_caller(site, users)
        other_site = SiteFactory()
        assert site.domain != other_site.domain

        # Same test as for "test_completed_method"
        LearnerCourseGradeMetricsFactory(site=other_site,
                                         sections_worked=1,
                                         sections_possible=1)
        not_completed_lcgm = [LearnerCourseGradeMetricsFactory(
            site=site,
            sections_worked=1,
            sections_possible=5) for i in range(2)]
        LearnerCourseGradeMetricsFactory(site=site,
                                         sections_worked=5,
                                         sections_possible=5)

        request_path = self.base_request_path + '?exclude_completed=True'
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=site,
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check keys
        result_ids = [obj['id'] for obj in results]
        assert set(result_ids) == set([obj.id for obj in not_completed_lcgm])
        # Spot check the first record
        obj = LearnerCourseGradeMetrics.objects.get(id=results[0]['id'])
        self.check_serialized_data(results[0], obj)

    def test_completed_ids_method(self, monkeypatch, enrollment_test_data):
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']
        caller = self.make_caller(site, users)
        other_site = SiteFactory()
        assert site.domain != other_site.domain
        LearnerCourseGradeMetricsFactory(site=other_site,
                                         sections_worked=1,
                                         sections_possible=1)
        # Create an incomplete LCGM rec for our site
        LearnerCourseGradeMetricsFactory(site=site,
                                         sections_worked=1,
                                         sections_possible=5)
        completed_lcgm = [LearnerCourseGradeMetricsFactory(site=site,
                                                           sections_worked=5,
                                                           sections_possible=5)
                          for i in range(3)]

        request_path = self.base_request_path + '/completed_ids/'
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=site,
                                     caller=caller,
                                     action='completed_ids')
        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check that the results have our expected keys and only our expected keys
        res_keys_list = [list(elem.keys()) for elem in results]
        results_key_set = set([item for sublist in res_keys_list for item in sublist])
        assert results_key_set == set(['course_id', 'user_id'])

        # Check that we have the data we're looking for
        results_values = [list(elem.values()) for elem in results]
        expected_values = [[obj.course_id, obj.user_id] for obj in completed_lcgm]
        assert set(map(tuple, results_values)) == set(map(tuple, expected_values))

    def test_completed_method(self, monkeypatch, enrollment_test_data):
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']
        caller = self.make_caller(site, users)
        other_site = SiteFactory()
        assert site.domain != other_site.domain
        # Create an LCGM record for the other site
        LearnerCourseGradeMetricsFactory(site=other_site,
                                         sections_worked=1,
                                         sections_possible=1)
        # Create an LCGM record for our site that is not completed
        LearnerCourseGradeMetricsFactory(site=site,
                                         sections_worked=1,
                                         sections_possible=5)
        completed_lcgm = [LearnerCourseGradeMetricsFactory(site=site,
                                                           sections_worked=5,
                                                           sections_possible=5)
                          for i in range(3)]

        request_path = self.base_request_path + '/completed/'
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=site,
                                     caller=caller,
                                     action='completed')
        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check keys
        result_ids = [obj['id'] for obj in results]
        assert set(result_ids) == set([obj.id for obj in completed_lcgm])
        # Spot check the first record
        obj = LearnerCourseGradeMetrics.objects.get(id=results[0]['id'])
        self.check_serialized_data(results[0], obj)

    @pytest.mark.parametrize('action', ['completed', 'completed_ids'])
    def test_no_paginate(self, monkeypatch, enrollment_test_data, action):

        site = enrollment_test_data['site']
        users = enrollment_test_data['users']
        caller = self.make_caller(site, users)
        request_path = '{}/{}/'.format(self.base_request_path, action)
        monkeypatch.setattr(EnrollmentMetricsViewSet, 'paginate_queryset',
                            lambda self, qs: None)
        with mock.patch.object(self.view_class, 'get_paginated_response') as paginate_check:
            response = self.make_request(request_path=request_path,
                                         monkeypatch=monkeypatch,
                                         site=site,
                                         caller=caller,
                                         action=action)
            assert response.status_code == status.HTTP_200_OK
            assert not is_response_paginated(response.data)
            assert not paginate_check.called
