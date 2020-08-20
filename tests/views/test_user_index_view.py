'''Tests Figures UserIndexView class

'''

from __future__ import absolute_import
import pytest

from django.contrib.auth import get_user_model
from django.db.models import F

from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from figures.helpers import is_multisite
from figures.views import UserIndexViewSet

from tests.factories import (
    OrganizationFactory,
    UserFactory,
)
from tests.views.base import BaseViewTest
from tests.helpers import organizations_support_sites

if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory


USER_DATA = [
    {'id': 101, 'username': u'alpha', 'fullname': u'Alpha One',
     'is_active': True, 'country': 'CA'},
    {'id': 102, 'username': u'alpha02', 'fullname': u'Alpha Two', 'is_active': False, 'country': 'UK'},
    {'id': 103, 'username': u'bravo', 'fullname': u'Bravo One', 'is_active': True, 'country': 'US'},
    {'id': 104, 'username': u'bravo02', 'fullname': u'Bravo Two', 'is_active': True, 'country': 'UY'},
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
class TestUserIndexViewSet(BaseViewTest):
    '''Tests the UserIndexView view class
    '''

    request_path = 'api/user-index/'
    view_class = UserIndexViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db):
        super(TestUserIndexViewSet, self).setup(db)
        self.users = [make_user(**data) for data in USER_DATA]
        self.usernames = [data['username'] for data in USER_DATA]
        self.expected_result_keys = ['id', 'username', 'fullname']
        if organizations_support_sites():
            self.organization = OrganizationFactory(sites=[self.site])
            for user in self.users:
                UserOrganizationMappingFactory(user=user,
                                               organization=self.organization)
        assert len(self.users) == len(USER_DATA)

    def get_expected_results(self, **filter):
        '''returns a list of dicts of the filtered user data
        
        '''
        return list(
            get_user_model().objects.filter(**filter).annotate(
                fullname=F('profile__name')).values(*self.expected_result_keys))

    # This test fails on 'assert 1'. More users are added after setup called
    @pytest.mark.xfail
    @pytest.mark.parametrize('query_params, filter_args', [
        ('', {}),
        ('?is_active=False', {'is_active': False}),
        ('?country=UY', {'profile__country': 'UY'}),
        # test lowercase is supported for country query param
        ('?country=uy', {'profile__country': 'UY'}),
        ])
    def test_get_user_index(self, query_params, filter_args):
        '''Tests retrieving a list of users with abbreviated details

        The fields in each returned record are identified by
            `figures.serializers.UserIndexSerializer`

        '''
        assert get_user_model().objects.count() == len(self.users), 'assert 1'
        expected_data = self.get_expected_results(**filter_args)
        assert get_user_model().objects.count() == len(self.users), 'assert 2'
        request = APIRequestFactory().get(
            self.request_path + query_params)
        force_authenticate(request, user=self.staff_user)
        view = self.view_class.as_view({'get':'list'})
        response = view(request)
        assert response.status_code == 200

        # Expect the following format for pagination
        # {
        #     "count": 2,
        #     "next": null, # or a url
        #     "previous": null, # or a url
        #     "results": [
        #     ...           # list of the results
        #     ]
        # }
        assert set(response.data.keys()) == set(
            ['count', 'next', 'previous', 'results',])

        assert len(response.data['results']) == len(expected_data)
        for rec in response.data['results']:
            match_rec = next((item for item in expected_data 
                if item['username'] == rec['username']))
            assert rec == match_rec
