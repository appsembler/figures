"""Tests Figures course monthly metrics viewset
"""

from __future__ import absolute_import
from faker import Faker
import pytest

import django.contrib.sites.shortcuts
from django.utils.timezone import utc
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from figures.views import CourseMonthlyMetricsViewSet

from tests.factories import (
    CourseOverviewFactory,
    CourseEnrollmentFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
    SiteFactory,
    UserFactory,
)
from tests.helpers import organizations_support_sites
from tests.views.base import BaseViewTest
from six.moves import range
from six.moves import zip

fake = Faker()


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


def generate_date_series(months_back=6, count=20):
    """

    """
    start_date = '-{months_back}M'.format(months_back=months_back)
    date_series = [fake.date_time_between(start_date=start_date,
                                          end_date='now',
                                          tzinfo=utc) for i in range(count)]
    date_series.sort()
    return date_series


@pytest.fixture
def course_test_data():
    """Temporary fixture. Will remove as we abstract testing
    """
    months_back = 6
    site = SiteFactory()
    course_overview = CourseOverviewFactory()
    if organizations_support_sites():
        org = OrganizationFactory(sites=[site])
    else:
        org = OrganizationFactory()

    OrganizationCourseFactory(organization=org,
                              course_id=str(course_overview.id))

    enrollments = [CourseEnrollmentFactory(
        course_id=course_overview.id) for i in range(3)]

    users = [enrollment.user for enrollment in enrollments]
    student_modules = []
    dates = generate_date_series(months_back=months_back)
    assert dates
    data_spec = list(zip(dates, list(range(months_back))))

    return dict(
        site=site,
        org=org,
        users=users,
        course_overview=course_overview,
        enrollments=enrollments,
        student_modules=student_modules,
        months_back=months_back,
        dates=dates,
        data_spec=data_spec,
    )


@pytest.fixture
def sog_data():
    """Fixture to create site, organization, and course overview

    This fixture exists mostly to help abstract multisite handing from tests

    Returns a dict of 'site', 'organization', and 'course_overview' objects
    """
    site = SiteFactory()
    course_overview = CourseOverviewFactory()
    if organizations_support_sites():
        organization = OrganizationFactory(sites=[site])
    else:
        organization = OrganizationFactory()
    OrganizationCourseFactory(organization=organization,
                              course_id=str(course_overview.id))
    return dict(
        site=site,
        organization=organization,
        course_overview=course_overview)


@pytest.mark.django_db
class TestCourseMonthlyMetricsViewSet(BaseViewTest):
    """Tests the Course Monthly Metrics set of endpoints

    TODO: DRY up the code, there is much duplication here

    """
    base_request_path = 'api/course-monthly-metrics/'
    view_class = CourseMonthlyMetricsViewSet
    months_back = 6

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        if organizations_support_sites():
            settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        super(TestCourseMonthlyMetricsViewSet, self).setup(db)

    def check_response(self, response, endpoint):
        """Helper method to reduce duplication
        """
        assert response.status_code == status.HTTP_200_OK
        assert endpoint in list(response.data.keys())
        history_list = response.data[endpoint]['history']

        # check that we have the current month and an element for each prior
        # month for N months back where N is `months_back`
        assert len(history_list) == self.months_back + 1
        for rec in history_list:
            assert all
            (key in rec for key in ('period', 'value'))
        return True

    def test_list_method(self, monkeypatch, course_test_data):
        """
        We need to add pagination to the list method and add that to the test
        """
        site = course_test_data['site']
        users = course_test_data['users']
        course_overview = course_test_data['course_overview']

        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=users)
        else:
            caller = UserFactory(is_staff=True)

        request = APIRequestFactory().get(self.base_request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_method(self, monkeypatch, course_test_data):
        site = course_test_data['site']
        users = course_test_data['users']
        course_overview = course_test_data['course_overview']

        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=users)
        else:
            caller = UserFactory(is_staff=True)

        request_path = self.base_request_path
        request = APIRequestFactory().get(request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'retrieve'})
        response = view(request, pk=str(course_overview.id))
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize('invalid_course_id', [
            '',
            'invalid-string',
            'course-v1:NothingToSeeHere+NTS+42',
        ])
    def test_retrieve_invalid_course_id(self, monkeypatch, course_test_data,
                                        invalid_course_id):
        """Tests that invalid course ids return '404 NOT FOUND'
        """
        site = course_test_data['site']
        users = course_test_data['users']
        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=users)
        else:
            caller = UserFactory(is_staff=True)

        request_path = self.base_request_path
        request = APIRequestFactory().get(request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'retrieve'})
        response = view(request, pk=invalid_course_id)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_active_users(self, monkeypatch, sog_data):
        site = sog_data['site']
        course_overview = sog_data['course_overview']
        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=[])
        else:
            caller = UserFactory(is_staff=True)

        expected_response = 'active_users history metric data'

        def mock_get_course_mau_history_metrics(**kwargs):
            return expected_response

        monkeypatch.setattr('figures.views.metrics.get_course_mau_history_metrics',
                            mock_get_course_mau_history_metrics)

        request_path = self.base_request_path + str(course_overview.id) + '/active_users/'
        request = APIRequestFactory().get(request_path)

        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'active_users'})
        response = view(request, pk=str(course_overview.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['active_users'] == expected_response

    def test_course_enrollments(self, monkeypatch, sog_data):
        site = sog_data['site']
        course_overview = sog_data['course_overview']
        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=[])
        else:
            caller = UserFactory(is_staff=True)

        expected_response = 'course_enrollments history metric data'

        def mock_get_course_history_metric(**kwargs):
            return expected_response

        monkeypatch.setattr('figures.views.get_course_history_metric',
                            mock_get_course_history_metric)

        request_path = self.base_request_path + str(course_overview.id) + '/course_enrollments/'
        request = APIRequestFactory().get(request_path)

        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'course_enrollments'})
        response = view(request, pk=str(course_overview.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['course_enrollments'] == expected_response

    def test_num_learners_completed(self, monkeypatch, sog_data):
        site = sog_data['site']
        course_overview = sog_data['course_overview']
        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=[])
        else:
            caller = UserFactory(is_staff=True)

        expected_response = 'num_learners_completed history metric data'

        def mock_get_course_history_metric(**kwargs):
            return expected_response

        monkeypatch.setattr('figures.views.get_course_history_metric',
                            mock_get_course_history_metric)

        request_path = self.base_request_path + str(course_overview.id) + '/num_learners_completed/'
        request = APIRequestFactory().get(request_path)

        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'num_learners_completed'})
        response = view(request, pk=str(course_overview.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['num_learners_completed'] == expected_response

    def test_avg_days_to_complete(self, monkeypatch, sog_data):
        site = sog_data['site']
        course_overview = sog_data['course_overview']
        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=[])
        else:
            caller = UserFactory(is_staff=True)

        expected_response = 'avg_days_to_complete history metric data'

        def mock_get_course_history_metric(**kwargs):
            return expected_response

        monkeypatch.setattr('figures.views.get_course_history_metric',
                            mock_get_course_history_metric)

        request_path = self.base_request_path + str(course_overview.id) + '/avg_days_to_complete/'
        request = APIRequestFactory().get(request_path)

        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'avg_days_to_complete'})
        response = view(request, pk=str(course_overview.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['avg_days_to_complete'] == expected_response

    def test_avg_progress(self, monkeypatch, sog_data):
        site = sog_data['site']
        course_overview = sog_data['course_overview']
        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=[])
        else:
            caller = UserFactory(is_staff=True)

        expected_response = 'avg_progress history metric data'

        def mock_get_course_history_metric(**kwargs):
            return expected_response

        monkeypatch.setattr('figures.views.get_course_history_metric',
                            mock_get_course_history_metric)

        request_path = self.base_request_path + str(course_overview.id) + '/avg_progress/'
        request = APIRequestFactory().get(request_path)

        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'avg_progress'})
        response = view(request, pk=str(course_overview.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['avg_progress'] == expected_response
