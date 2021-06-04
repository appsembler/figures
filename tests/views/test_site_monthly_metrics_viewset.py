"""
Tests Figures site monthly metrics viewset
"""

from __future__ import absolute_import
from datetime import datetime
from faker import Faker
import pytest

import django.contrib.sites.shortcuts
from django.utils.timezone import utc
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from figures.helpers import is_multisite
from figures.views import SiteMonthlyMetricsViewSet

from tests.factories import (
    OrganizationFactory,
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
def user_reg_test_data():
    """
    Creates a set of users registering over a time period
    """
    site = SiteFactory()
    today = datetime.utcnow().date()
    months_back = 6
    users = []
    dates = generate_date_series(months_back=months_back)
    assert dates
    data_spec = list(zip(dates, list(range(months_back))))

    for reg_date, reg_count in data_spec:
        users += [UserFactory(date_joined=reg_date) for i in range(reg_count)]
    return dict(
        site=site,
        users=users,
        dates=dates,
        months_back=months_back,
    )


@pytest.mark.django_db
class TestSiteMonthlyMetricsViewSet(BaseViewTest):
    """
    TODO:
    * Refactor tests to use common code
    """
    request_path = 'api/site-metrics'
    view_class = SiteMonthlyMetricsViewSet
    months_back = 6

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        if organizations_support_sites():
            settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        super(TestSiteMonthlyMetricsViewSet, self).setup(db)

    def check_response(self, response, endpoint):
        assert response.status_code == status.HTTP_200_OK
        assert endpoint in list(response.data.keys())
        current_month_count = response.data[endpoint]['current_month']
        history_list = response.data[endpoint]['history']

        # check that we have the current month and an element for each prior
        # month for N months back where N is `months_back`
        assert len(history_list) == self.months_back
        for rec in history_list:
            assert all (key in rec for key in ('period', 'value'))
        return True

    def run_request(self, endpoint, user_reg_test_data):
        """
        Stub
        """
        pass

    @pytest.mark.skip(reason='We need to confirm who is in total registered users')
    def test_registered_learners(self, monkeypatch, user_reg_test_data):
        """
        TODO: create filter and query param for getting unique users who are
        enrolled in a course and not course staff
        """
        pass

    def test_registered_learners(self, monkeypatch, user_reg_test_data):
        """

        Example response data:
            {'registered_users': {'current_month': 20,
            'history': [
            {'period': '2019/08', 'value': 3},
            {'period': '2019/09', 'value': 4},
            {'period': '2019/10', 'value': 7},
            {'period': '2019/11', 'value': 11},
            {'period': '2019/12', 'value': 20},
            {'period': '2020/01', 'value': 20},
            {'period': '2020/02', 'value': 20}]}}
        """
        request_method = 'get'
        endpoint = 'registered_users'
        site = user_reg_test_data['site']
        users = user_reg_test_data['users']
        dates = user_reg_test_data['dates']
        months_back = user_reg_test_data['months_back']

        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=users)
        else:
            caller = UserFactory(is_staff=True)

        request = APIRequestFactory().get(self.request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({request_method: endpoint})
        response = view(request)
        assert self.check_response(response=response, endpoint=endpoint)

        # Initially we have a basic structure check
        # TODO: validate each month's period string and value

    def test_new_users(self, monkeypatch, user_reg_test_data):
        endpoint = 'new_users'
        request_method = 'get'
        site = user_reg_test_data['site']
        users = user_reg_test_data['users']
        dates = user_reg_test_data['dates']
        months_back = user_reg_test_data['months_back']

        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=users)
        else:
            caller = UserFactory(is_staff=True)

        request = APIRequestFactory().get(self.request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({request_method: endpoint})
        response = view(request)
        assert self.check_response(response=response, endpoint=endpoint)

    def test_course_completions(self, monkeypatch, user_reg_test_data):
        endpoint = 'course_completions'
        request_method = 'get'
        site = user_reg_test_data['site']
        users = user_reg_test_data['users']
        dates = user_reg_test_data['dates']
        months_back = user_reg_test_data['months_back']

        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=users)
        else:
            caller = UserFactory(is_staff=True)

        request = APIRequestFactory().get(self.request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({request_method: endpoint})
        response = view(request)
        assert self.check_response(response=response, endpoint=endpoint)

    def test_course_enrollments(self, monkeypatch, user_reg_test_data):
        endpoint = 'course_enrollments'
        request_method = 'get'
        site = user_reg_test_data['site']
        users = user_reg_test_data['users']
        dates = user_reg_test_data['dates']
        months_back = user_reg_test_data['months_back']

        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=users)
        else:
            caller = UserFactory(is_staff=True)

        request = APIRequestFactory().get(self.request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({request_method: endpoint})
        response = view(request)
        assert self.check_response(response=response, endpoint=endpoint)

    def test_site_courses(self, monkeypatch, user_reg_test_data):
        endpoint = 'site_courses'
        request_method = 'get'
        site = user_reg_test_data['site']
        users = user_reg_test_data['users']
        dates = user_reg_test_data['dates']
        months_back = user_reg_test_data['months_back']

        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=users)
        else:
            caller = UserFactory(is_staff=True)

        request = APIRequestFactory().get(self.request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({request_method: endpoint})
        response = view(request)
        assert self.check_response(response=response, endpoint=endpoint)

    def test_active_users(self, monkeypatch, user_reg_test_data):
        endpoint = 'active_users'
        request_method = 'get'
        site = user_reg_test_data['site']

        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=[])
        else:
            caller = UserFactory(is_staff=True)

        expected_response = 'active_users history metric data'
        monkeypatch.setattr('figures.views.metrics.get_site_mau_history_metrics',
                            lambda **_kwargs: expected_response)

        request = APIRequestFactory().get(self.request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({request_method: endpoint})
        response = view(request)

        assert response.data['active_users'] == expected_response

    @pytest.mark.skip(reason='test this after other module tests pass')
    def test_run_request(self, monkeypatch, user_reg_test_data):
        self.run_request(endpoint='registered_users',
                    user_reg_test_data=user_reg_test_data)
