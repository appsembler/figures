'''Test the permission classes we define in Figures

'''

import mock
import pytest

from django.contrib.auth import get_user_model

from rest_framework.test import APIRequestFactory

import figures.permissions
import figures.settings

from tests.factories import SiteFactory, UserFactory, UserSiteMappingFactory
from tests.views.helpers import create_test_users

@pytest.mark.django_db
class TestPermissions(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.callers = create_test_users()

    @pytest.mark.parametrize('username, allow', [
        ('regular_user', False),
        ('staff_user', True),
        ('super_user', True),
        ('superstaff_user', True),
    ])
    def test_is_staff_user(self, username, allow):
        '''Tests a set of users against the IsStaffUser permission class
        '''
        request = APIRequestFactory().get('/')
        request.user = get_user_model().objects.get(username=username)
        permission = figures.permissions.IsStaffUser().has_permission(
            request, None)
        assert permission == allow

        # verify that inactive users are denied permission
        request.user.is_active = False
        permission = figures.permissions.IsStaffUser().has_permission(
            request, None)
        assert permission == False


@pytest.mark.django_db
class TestSiteAdminPermissions(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = SiteFactory()
        self.callers = [
            UserFactory(username='alpha_nonadmin'),
            UserFactory(username='alpha_site_admin'),
        ]

        self.user_site_mappings = [
            UserSiteMappingFactory(user=self.callers[0],
                site=self.site),
            UserSiteMappingFactory(
                user=self.callers[1],
                site=self.site,
                is_amc_admin=True)
        ]

    @mock.patch('figures.settings')
    @pytest.mark.parametrize('username, allow', [
        ('alpha_nonadmin', False),
        ('alpha_site_admin', True)])
    def test_is_site_admin_user(self, figures_settings, username, allow):
        request = APIRequestFactory().get('/')
        request.META['HTTP_HOST'] = self.site.domain
        request.user = get_user_model().objects.get(username=username)
        figures_settings.DEFAULT_IS_MULTI_TENANT = True
        permission = figures.permissions.IsSiteAdminUser().has_permission(
            request, None)
        assert permission == allow

