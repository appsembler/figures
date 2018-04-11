'''Unit tests for the user-index view

'''

import pytest

from django.contrib.auth import get_user_model
from django.db.models import F

from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from edx_figures.views import (
    UserIndexView,
    )

from ..factories import UserFactory

USER_DATA = [
    {'id': 1, 'username': u'alpha', 'fullname': u'Alpha One',
     'is_active': True, 'country': 'CA'},
    {'id': 2, 'username': u'alpha02', 'fullname': u'Alpha Two', 'is_active': False, 'country': 'UK'},
    {'id': 3, 'username': u'bravo', 'fullname': u'Bravo One', 'is_active': True, 'country': 'US'},
    {'id': 4, 'username': u'bravo02', 'fullname': u'Bravo Two', 'is_active': True, 'country': 'UY'},
]

def make_user(**kwargs):
    return UserFactory(
        id=kwargs['id'],
        username=kwargs['username'],
        profile__name=kwargs['fullname'],
        profile__country=kwargs['country'],
        is_active=kwargs['is_active'],
    )


@pytest.mark.django_db
class TestUserIndexView(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.users = [make_user(**data) for data in USER_DATA]
        self.expected_result_keys = ['id', 'username', 'fullname']

    def get_expected_results(self, **filter):
        '''returns a list of dicts of the filtered user data

        '''
        return list(
            get_user_model().objects.filter(**filter).annotate(
                fullname=F('profile__name')).values(*self.expected_result_keys))

    @pytest.mark.parametrize('endpoint, filter', [
        ('api/user-index', {}),
        ('api/user-index/?is_active=False', {'is_active': False}),
        ('api/user-index/?country=UY', {'profile__country': 'UY'}),
        # test lowercase is supported for country query param
        ('api/user-index/?country=uy', {'profile__country': 'UY'}),
        ])
    def test_get_user_index(self, endpoint, filter):
        '''Tests retrieving a list of users with abbreviated details

        The fields in each returned record are identified by
            `edx_figures.serializers.UserIndexSerializer`

        '''
        expected_data = self.get_expected_results(**filter)

        factory = APIRequestFactory()
        request = factory.get(endpoint)
        force_authenticate(request, user=self.users[0])
        view = UserIndexView.as_view()
        response = view(request)
        assert response.status_code == 200
        assert len(response.data) == len(expected_data)
        assert response.data == expected_data
