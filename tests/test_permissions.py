'''Test the permission classes we define in Figures

'''

import pytest

from django.contrib.auth import get_user_model

from rest_framework.test import APIRequestFactory

from figures.permissions import IsStaffUser

from tests.factories import UserFactory
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
        permission = IsStaffUser().has_permission(request, None)
        assert permission == allow

        # verify that inactive users are denied permission
        request.user.is_active = False
        permission = IsStaffUser().has_permission(request, None)
        assert permission == False
