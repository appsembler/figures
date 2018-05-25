'''Tests Figures CourseDailyMetricsViewSet class

'''

import datetime
from decimal import Decimal
from dateutil.parser import parse
#from dateutil.rrule import rrule, DAILY
import pytest

from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from figures.models import CourseDailyMetrics
from figures.views import CourseDailyMetricsViewSet

from tests.factories import CourseDailyMetricsFactory, UserFactory
from tests.helpers import create_metrics_model_timeseries


@pytest.mark.django_db
class TestCourseDailyMetricsView(object):
    '''Tests the viewset for CourseDailyMetrics

    Notes:
    * This test class duplicates some of the code in 
        test_serializers.TestCourseDailyMetricsSerializer
    * This test class shares duplicate code with TestSiteDailyMetricsView. So
      we probably want to create a common test class for the common code

    We might want to do the date handling/comparing code as a mix-in

    TODO: After we finish and commit the view test for this, set the serialization
    type for the dates. This should simplify this a lot 
    # http://www.django-rest-framework.org/api-guide/fields/#date-and-time-fields
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.first_day = parse('2018-01-01')
        self.last_day = parse('2018-03-31')
        self.date_fields = set(['date_for', 'created', 'modified',])
        self.expected_results_keys = set([o.name for o in CourseDailyMetrics._meta.fields])
        field_names = (o.name for o in CourseDailyMetrics._meta.fields
            if o.name not in self.date_fields )

        self.metrics = create_metrics_model_timeseries(
            CourseDailyMetricsFactory, self.first_day, self.last_day)

    def assert_response_equal(self, response_data, obj):
        '''Convenience method to compare serialized data to model object
        '''
        # Hack: Check date and datetime values explicitly
        assert response_data['date_for'] == str(obj.date_for)
        assert parse(response_data['created']) == obj.created
        assert parse(response_data['modified']) == obj.modified

        for field_name in (self.expected_results_keys - self.date_fields):
            obj_field = getattr(obj, field_name)
            if (type(response_data) in (float, Decimal,) or 
                type(obj_field) in (float, Decimal,)):
                assert float(response_data[field_name]) == pytest.approx(obj_field)
            else:
                assert response_data[field_name] == obj_field

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
        endpoint = 'api/course-daily-metrics/?date_0={}&date_1={}'.format(
            first_day, last_day)

        expected_data = CourseDailyMetrics.objects.filter(
            date_for__range=(first_day, last_day))
        factory = APIRequestFactory()
        request = factory.get(endpoint)
        force_authenticate(request, user=UserFactory())
        view = CourseDailyMetricsViewSet.as_view({'get':'list'})
        response = view(request)
        assert response.status_code == 200
        assert len(response.data) == expected_data.count()

        # Hack: Check date and datetime values explicitly
        for data in response.data:
            db_rec = expected_data.get(id=data['id'])
            self.assert_response_equal(data, db_rec)

    @pytest.mark.parametrize('data', [
        ( dict(
            date_for='2020-01-01',
            course_id='course-v1:SomeOrg+ABC01+2121',
            enrollment_count=11,
            active_learners_today=1,
            average_progress=0.5,
            average_days_to_complete=5,
            num_learners_completed=10
            )
        ),
    ])
    def test_create(self, data):
        factory = APIRequestFactory()

        # Might not need to set format='json'
        request = factory.post('api/course-daily-metrics/', data, format='json')
        force_authenticate(request, user=UserFactory())
        view = CourseDailyMetricsViewSet.as_view({'post': 'create'})
        
        response = view(request)

        assert response.status_code == 201
        obj = CourseDailyMetrics.objects.get(
            date_for=data['date_for'],
            course_id=data['course_id'])
        self.assert_response_equal(response.data, obj)
