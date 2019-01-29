'''Test the permission classes we define in Figures

'''

import mock
import pytest

from django.contrib.auth import get_user_model

from rest_framework.test import APIRequestFactory

import figures.permissions
import figures.settings
# import figures.sites

from tests.factories import OrganizationFactory, SiteFactory, UserFactory

# For multisite testing
try:
    from tests.factories import UserOrganizationMappingFactory
except ImportError:
    pass

from tests.helpers import organizations_support_sites
from tests.views.helpers import create_test_users


@pytest.mark.django_db
class TestPermissionsForStandaloneMode(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.callers = create_test_users()

    @pytest.mark.parametrize('username, allow', [
        ('regular_user', False),
        ('staff_user', True),
        ('super_user', True),
        ('superstaff_user', True),
    ])
    def test_is_site_admin_user(self, username, allow):
        """Tests a set of users against the IsSiteAdminUser permission class
        """
        request = APIRequestFactory().get('/')
        request.user = get_user_model().objects.get(username=username)
        permission = figures.permissions.IsSiteAdminUser().has_permission(request, None)
        assert permission == allow, 'username: "{}"'.format(username)

        # verify that inactive users are denied permission
        request.user.is_active = False
        permission = figures.permissions.IsSiteAdminUser().has_permission(request, None)
        assert permission is False, 'username: "{}"'.format(username)


@pytest.mark.skipif(not organizations_support_sites(),
                    reason='Organizations support sites')
@pytest.mark.django_db
class TestSiteAdminPermissionsForMultisiteMode(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = SiteFactory()
        self.organization = OrganizationFactory(sites=[self.site])
        self.callers = [
            UserFactory(username='alpha_nonadmin'),
            UserFactory(username='alpha_site_admin'),
            UserFactory(username='nosite_staff'),
        ]
        self.user_organization_mappings = [
            UserOrganizationMappingFactory(
                user=self.callers[0],
                organization=self.organization),
            UserOrganizationMappingFactory(
                user=self.callers[1],
                organization=self.organization,
                is_amc_admin=True)
        ]
        self.env_tokens = {'IS_FIGURES_MULTISITE': True}

    # @mock.patch('figures.settings')
    @pytest.mark.parametrize('username, allow', [
        ('alpha_nonadmin', False),
        ('alpha_site_admin', True),
        ('nosite_staff', False),
        ])
    # def test_is_site_admin_user(self, figures_settings, username, allow):
    def test_is_site_admin_user(self, monkeypatch, username, allow):
        def test_site(request):
            return self.site
        request = APIRequestFactory().get('/')
        request.META['HTTP_HOST'] = self.site.domain
        request.user = get_user_model().objects.get(username=username)
        monkeypatch.setattr(figures.sites, 'get_current_site', test_site)
        with mock.patch('figures.settings.env_tokens', self.env_tokens):
            assert figures.settings.is_multisite()

            permission = figures.permissions.IsSiteAdminUser().has_permission(
                request, None)
            assert permission == allow

            # verify that inactive users are denied permission
            request.user.is_active = False
            permission = figures.permissions.IsSiteAdminUser().has_permission(
                request, None)
            assert permission is False, 'username: "{}"'.format(username)

    def test_multiple_user_orgs(self, monkeypatch):
        def test_site(request):
            return self.site
        username = 'alpha_site_admin'
        request = APIRequestFactory().get('/')
        request.META['HTTP_HOST'] = self.site.domain
        request.user = get_user_model().objects.get(username=username)
        monkeypatch.setattr(figures.sites, 'get_current_site', test_site)
        with mock.patch('figures.settings.env_tokens', self.env_tokens):
            assert figures.settings.is_multisite()
            org2 = OrganizationFactory(sites=[self.site])
            UserOrganizationMappingFactory(user=request.user, organization=org2),
            with pytest.raises(figures.permissions.MultipleOrgsPerUserNotSupported):
                figures.permissions.IsSiteAdminUser().has_permission(request, None)
