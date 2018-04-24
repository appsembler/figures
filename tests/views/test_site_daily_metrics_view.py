'''Unit tests for the site daily metrics view

'''

import datetime
from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY
import pytest

from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from edx_figures.models import SiteDailyMetrics
from edx_figures.views import SiteDailyMetricsViewSet

from tests.factories import SiteDailyMetricsFactory, UserFactory

TEST_DATA = [
    {}

]

def generate_sdm_series(first_day, last_day):

    return [SiteDailyMetricsFactory(date_for=dt) 
        for dt in rrule(DAILY, dtstart=first_day, until=last_day)]


@pytest.mark.django_db
class TestSiteDailyMetricsView(object):
    '''

    Note: This test class duplicates some of the code in 
        test_serializers.TestSiteDailyMetricsSerializer

    We might want to do the date handling/comparing code as a mix-in

    TODO: AFter we finish and commit the view test for this, set the serialization
    type for the dates. This should simplify this a lot 
    # http://www.django-rest-framework.org/api-guide/fields/#date-and-time-fields

    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
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
        ('2018-02-01', '2018-02-28'),
    ])
    def test_get_by_date_range(self, first_day, last_day):
        '''
        Note: This test is sensitive in the order data are compared. It expects
        that records are retrieved by date_for, descending.

        TODO: Add more date ranges
        '''
        first_day='2018-02-01'
        last_day='2018-02-28'
        endpoint = 'api/site-daily-metrics/?date_0={}&date_1={}'.format(
            first_day, last_day)

        expected_data = SiteDailyMetrics.objects.filter(
            date_for__range=(first_day, last_day))
        factory = APIRequestFactory()
        request = factory.get(endpoint)
        force_authenticate(request, user=UserFactory())
        view = SiteDailyMetricsViewSet.as_view({'get':'list'})
        response = view(request)
        assert response.status_code == 200
        assert len(response.data) == expected_data.count()

        # Hack: Check date and datetime values explicitly
        for data in response.data:
            db_rec = expected_data.get(id=data['id'])
            assert data['date_for'] == str(db_rec.date_for)
            assert parse(data['created']) == db_rec.created
            assert parse(data['modified']) == db_rec.modified

        field_names = self.expected_results_keys - self.date_fields

        for field_name in (self.expected_results_keys - self.date_fields):
            assert data[field_name] == getattr(db_rec,field_name)

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
        factory = APIRequestFactory()

        # Might not need to set format='json'
        request = factory.post('api/site-daily-metrics/', data, format='json')
        force_authenticate(request, user=UserFactory())
        view = SiteDailyMetricsViewSet.as_view({'post': 'create'})
        
        response = view(request)

        assert response.status_code == 201
        assert 'id' in response.data.keys()
        for key in data.keys():
            assert response.data[key] == data[key]
