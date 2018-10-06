'''Tests Figures SiteDailyMetricsViewSet class

'''

import datetime
from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY
import pytest

from django.contrib.auth import get_user_model

from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from figures.models import SiteDailyMetrics
from figures.pagination import FiguresLimitOffsetPagination
from figures.views import SiteDailyMetricsViewSet

from tests.factories import SiteDailyMetricsFactory, UserFactory
from tests.views.base import BaseViewTest


TEST_DATA = [
    {}

]

def generate_sdm_series(first_day, last_day):

    return [SiteDailyMetricsFactory(date_for=dt) 
        for dt in rrule(DAILY, dtstart=first_day, until=last_day)]


@pytest.mark.django_db
class TestSiteDailyMetricsView(BaseViewTest):
    '''

    Note: This test class duplicates some of the code in 
        test_serializers.TestSiteDailyMetricsSerializer

    We might want to do the date handling/comparing code as a mix-in

    TODO: AFter we finish and commit the view test for this, set the serialization
    type for the dates. This should simplify this a lot 
    # http://www.django-rest-framework.org/api-guide/fields/#date-and-time-fields

    '''
    request_path = 'api/site-daily-metrics'
    view_class = SiteDailyMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db):
        super(TestSiteDailyMetricsView, self).setup(db)
        self.first_day = parse('2018-01-01')
        self.last_day = parse('2018-03-31')
        self.date_fields = set(['date_for', 'created', 'modified',])
        self.expected_results_keys = set([o.name for o in SiteDailyMetrics._meta.fields])
        field_names = (o.name for o in SiteDailyMetrics._meta.fields
            if o.name not in self.date_fields )

        self.metrics = generate_sdm_series(self.first_day, self.last_day)

    def test_get_last_day(self):
        pass

    @pytest.mark.parametrize('first_day, last_day', [
        ('2018-02-01', '2018-02-28',),
    ])
    def test_get_by_date_range(self, first_day, last_day):
        '''
        Note: This test is sensitive in the order data are compared. It expects
        that records are retrieved by date_for, descending.

        TODO: Add more date ranges
        '''
        first_day='2018-02-01'
        last_day='2018-02-28'
        endpoint = '{}?date_0={}&date_1={}'.format(
            self.request_path, first_day, last_day)

        expected_data = SiteDailyMetrics.objects.filter(
            date_for__range=(first_day, last_day))
        factory = APIRequestFactory()
        request = factory.get(endpoint)
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
        assert len(response.data['results']) == FiguresLimitOffsetPagination.default_limit

        # Hack: Check date and datetime values explicitly
        for data in response.data['results']:
            db_rec = expected_data.get(id=data['id'])
            assert data['date_for'] == str(db_rec.date_for)
            assert parse(data['created']) == db_rec.created
            assert parse(data['modified']) == db_rec.modified

        field_names = self.expected_results_keys - self.date_fields

        for field_name in (self.expected_results_keys - self.date_fields):
            assert data[field_name] == getattr(db_rec,field_name)

    # @pytest.mark.parametrize('username, status_code', [
    #     ('regular_user', 403),
    #     ('staff_user', 200),
    #     ('super_user', 200),
    #     ('superstaff_user', 200),
    # ])
    # def test_get_authentication(self, username, status_code):
    #     factory = APIRequestFactory()
    #     request = factory.get('api/site-daily-metrics')
    #     user = get_user_model().objects.get(username='staff_user')
    #     force_authenticate(request, user=user)
    #     view = SiteDailyMetricsViewSet.as_view({'get':'list'})
    #     response = view(request)
    #     assert response.status_code == 200


    @pytest.mark.parametrize('data', [
        ( dict(
            date_for='2020-01-01',
            cumulative_active_user_count=1,
            todays_active_user_count=2,
            total_user_count=3,
            course_count=4,
            total_enrollment_count=5
            )
        ),
    ])
    def test_create(self, data):

        # Might not need to set format='json'
        request = APIRequestFactory().post(
            self.request_path, data, format='json')
        force_authenticate(request, user=self.staff_user)
        view = SiteDailyMetricsViewSet.as_view({'post': 'create'})
        response = view(request)

        assert response.status_code == 201
        assert 'id' in response.data.keys()
        for key in data.keys():
            assert response.data[key] == data[key]
