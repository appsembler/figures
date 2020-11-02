"""Tests Figures SiteViewSet

"""

from __future__ import absolute_import
import pytest

from django.contrib.sites.models import Site
import django.contrib.sites.shortcuts

from rest_framework.test import APIRequestFactory

from figures.views import SiteViewSet

from tests.factories import SiteFactory
from tests.views.base import BaseViewTest


@pytest.mark.django_db
class TestSiteViewSet(BaseViewTest):

    request_path = 'api/admin/sites/'
    view_class = SiteViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db):
        super(TestSiteViewSet, self).setup(db)
        assert Site.objects.count() == 1
        self.sites = [
            Site.objects.first(),
            SiteFactory(domain=u'alpha.test.site', name=u'Alpha Group'),
            SiteFactory(domain=u'bravo.test.site', name=u'Bravo Organization'),
        ]
        self.expected_result_keys = ['id', 'domain', 'name']

    def get_expected_results(self, **filter):
        """Returns a list of dicts of the filtered site data
        """
        return list(
            Site.objects.filter(**filter).values(*self.expected_result_keys))

    @pytest.mark.parametrize('query_params, filter_args', [
        ('', {}),
        ('?domain=bravo', {'domain__icontains': 'bravo'}),
        ('?name=alpha', {'name__icontains': 'alpha'})
        ])
    def test_get(self, query_params, filter_args):
        qp_msg = 'query_params={query_params}'
        expected_data = Site.objects.filter(**filter_args)
        request = APIRequestFactory().get(self.request_path + query_params)
        request.user = self.staff_user
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == 200, qp_msg.format(query_params=query_params)
        assert set(response.data.keys()) == set(
            ['count', 'next', 'previous', 'results'])
        assert len(response.data['results']) == len(expected_data), qp_msg.format(
            query_params=query_params)
        results = response.data['results']

        # Validate just the first object's structure
        for field_name in self.expected_result_keys:
            assert field_name in results[0]

        # Validate the ids match up
        expected_ids = expected_data.values_list('id', flat=True)
        actual_ids = [o['id'] for o in results]
        assert set(actual_ids) == set(expected_ids)

    def test_access_from_non_default_site(self, monkeypatch):
        """Validates view not accessible for an authorized user if not made in
        the default site
        """
        foo_site = SiteFactory(domain='foo.site', name='Foo Site')

        def test_site(request):
            return foo_site
        request = APIRequestFactory().get(self.request_path)
        request.META['HTTP_HOST'] = foo_site.domain
        request.user = self.staff_user
        monkeypatch.setattr(django.contrib.sites.shortcuts, 'get_current_site', test_site)
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == 403
