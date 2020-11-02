'''Test the Figures UI view

The ``TestFiguresHomeView`` test class requires that ``webpack-stats.json`` exists in order for Django Webpack Loader to find the front end assets. This file is created when ``npm run-script build`` is executed

'''

from __future__ import absolute_import
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.test import RequestFactory

try: 
    # Django 2.0+
    from django.urls import reverse
except ImportError:
    # Django <1.9
    from django.core.urlresolvers import reverse


import pytest

from figures.views import figures_home, UNAUTHORIZED_USER_REDIRECT_URL

from tests.factories import UserFactory
from tests.views.helpers import create_test_users
#
@pytest.mark.django_db
class TestFiguresHomeView(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.factory = RequestFactory()
        self.callers = create_test_users()
        self.callers.append(
            UserFactory(username='inactive_regular_user',
                is_active=False))
        self.callers.append(
            UserFactory(username='inactive_staff_user',
                is_active=False, is_staff=True))
        self.callers.append(
            UserFactory(username='inactive_super_user',
                is_active=False, is_superuser=True))
        self.callers.append(
            UserFactory(username='inactive_superstaff_user',
                is_active=False, is_staff=True, is_superuser=True))
        self.redirect_startswith = '/accounts/login/?next='

    def test_anonymous_user(self):
        '''Verify that anonymous users (not logged in) get redirected to login
        '''
        request = self.factory.get(reverse('figures-home'))
        request.user = AnonymousUser()
        response = figures_home(request)
        assert response.status_code == 302
        assert response['location'].startswith(self.redirect_startswith)

    @pytest.mark.parametrize('username, status_code', [
        ('regular_user', 302),
        ('inactive_staff_user', 302),
        ('staff_user', 200),
        ('inactive_super_user', 302),
        ('super_user', 200),
        ('inactive_superstaff_user', 302),
        ('superstaff_user', 200),
        ])
    def test_registered_users(self, username, status_code):
        '''Test that only active staff and superuser users can access the 
        Figures page and that users that don't pass the test get redirected
        to
        '''
        request = self.factory.get(reverse('figures-home'))
        request.user = get_user_model().objects.get(username=username)
        response = figures_home(request)
        assert response.status_code == status_code, "username={}".format(username)
        if status_code == 302:
            assert response['location'] == UNAUTHORIZED_USER_REDIRECT_URL
