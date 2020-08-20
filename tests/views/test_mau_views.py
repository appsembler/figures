
from __future__ import absolute_import
import pytest

import django.contrib.sites.shortcuts
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from figures.helpers import is_multisite
from figures.views import (
    CourseMauLiveMetricsViewSet,
    CourseMauMetricsViewSet,
    SiteMauLiveMetricsViewSet,
    SiteMauMetricsViewSet,
)

from tests.factories import UserFactory

from tests.helpers import organizations_support_sites
from tests.views.base import BaseViewTest


if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory


@pytest.mark.django_db
class TestSiteMauLiveMetricsViewSet(BaseViewTest):
    request_path = 'api/site-mau-live-metrics'
    view_class = SiteMauLiveMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        settings.FEATURES['FIGURES_IS_MULTISITE'] = organizations_support_sites()
        super(TestSiteMauLiveMetricsViewSet, self).setup(db)

    def test_list(self, monkeypatch, sm_test_data):

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
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCourseMauLiveMetricsViewSet(BaseViewTest):
    request_path = 'api/course-mau-live-metrics'
    view_class = CourseMauLiveMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        super(TestCourseMauLiveMetricsViewSet, self).setup(db)

    def test_retrieve(self, monkeypatch, sm_test_data):
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

    def test_list(self, monkeypatch, sm_test_data):
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


@pytest.mark.django_db
class TestSiteMauMetricsViewSet(BaseViewTest):
    request_path = 'api/site-mau-metrics'
    view_class = SiteMauMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        super(TestSiteMauMetricsViewSet, self).setup(db)

    def test_site_metrics_list(self, monkeypatch, sm_test_data):

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
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCourseMauMetricsViewSet(BaseViewTest):
    request_path = 'api/course-mau-metrics'
    view_class = CourseMauMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        super(TestCourseMauMetricsViewSet, self).setup(db)

    def test_site_metrics_list(self, monkeypatch, sm_test_data):

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
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)

        assert response.status_code == status.HTTP_200_OK
