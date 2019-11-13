
import pytest

import django.contrib.sites.shortcuts
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from figures.helpers import is_multisite
from figures.views import MauSiteMetricsViewSet, MauCourseMetricsViewSet

from tests.factories import UserFactory

from tests.helpers import organizations_support_sites
from tests.views.base import BaseViewTest

# from tests.test_mau import sm_test_data  # noqa: F401

if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory


@pytest.mark.django_db
class TestMauSiteMetricsViewSet(BaseViewTest):
    request_path = 'api/mau-site-metrics'
    view_class = MauSiteMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        super(TestMauSiteMetricsViewSet, self).setup(db)

        settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        is_ms = is_multisite()
        assert is_ms

    def test_site_metrics_happy_case(self, monkeypatch, sm_test_data):

        site = sm_test_data['site']
        org = sm_test_data['organization']
        if organizations_support_sites():
            caller = UserFactory()
            UserOrganizationMappingFactory(user=caller,
                                           organization=org,
                                           is_amc_admin=True)
        else:
            caller = UserFactory(is_staff=True)
        request = APIRequestFactory().get(self.request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'retrieve'})
        response = view(request)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestMauCourseMetricsViewSet(BaseViewTest):
    request_path = 'api/mau-course-metrics'
    view_class = MauCourseMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        super(TestMauCourseMetricsViewSet, self).setup(db)

        settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        is_ms = is_multisite()
        assert is_ms

    def test_course_metrics_retrieve(self, monkeypatch, sm_test_data):
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        site = sm_test_data['site']
        org = sm_test_data['organization']
        co = sm_test_data['course_overviews'][0]

        if organizations_support_sites():
            caller = UserFactory()
            UserOrganizationMappingFactory(user=caller,
                                           organization=org,
                                           is_amc_admin=True)
        else:
            caller = UserFactory(is_staff=True)

        request_path = self.request_path + '?pk=' + str(co.id)
        request = APIRequestFactory().get(request_path)
        request.META['HTTP_HOST'] = site.domain

        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'retrieve'})
        response = view(request, pk=str(co.id))

        assert response.status_code == status.HTTP_200_OK
        # TODO: Assert data are correct

    def test_course_metrics_list(self, monkeypatch, sm_test_data):
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        site = sm_test_data['site']
        org = sm_test_data['organization']
        co = sm_test_data['course_overviews'][0]

        if organizations_support_sites():
            caller = UserFactory()
            UserOrganizationMappingFactory(user=caller,
                                           organization=org,
                                           is_amc_admin=True)
        else:
            caller = UserFactory(is_staff=True)

        request_path = self.request_path
        request = APIRequestFactory().get(request_path)
        request.META['HTTP_HOST'] = site.domain

        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == status.HTTP_200_OK
        # TODO: Assert data are correct
