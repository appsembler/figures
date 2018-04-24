'''
Test the serializers in edx-figures



'''

from dateutil.parser import parse as dateutil_parse
import pytest

from django.db import models
from edx_figures.models import SiteDailyMetrics
from edx_figures.serializers import (
    UserIndexSerializer,
    SiteDailyMetricsSerializer,
)

from .factories import SiteDailyMetricsFactory, UserFactory

@pytest.mark.django_db
class TestUserIndexSerializer(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.user_attributes = {
            'username': 'alpha_one',
            'profile__name': 'Alpha One',
            'profile__country': 'CA',
        }
        self.user = UserFactory(**self.user_attributes)
        self.serializer = UserIndexSerializer(instance=self.user)

    def test_has_fields(self):
        '''Tests that the serialized UserIndex data has specific keys and values
        
        We use a set instead of just doing this:

            assert data.keys() == ['id', 'username', 'fullname', ]

        because we can't guarentee order. See:
            https://docs.python.org/2/library/stdtypes.html#dict.items
        '''
        data = self.serializer.data

        assert set(data.keys()) == set(['id', 'username', 'fullname', ])
        
        # This is to make sure that the serializer retrieves the correct nested
        # model (UserProfile) data
        assert data['fullname'] == 'Alpha One'


@pytest.mark.django_db
class TestSiteDailyMetricsSerializer(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        '''

        '''
        self.date_fields = set(['date_for', 'created', 'modified',])
        self.expected_results_keys = set([o.name for o in SiteDailyMetrics._meta.fields])
        field_names = (o.name for o in SiteDailyMetrics._meta.fields
            if o.name not in self.date_fields )
        self.site_daily_metrics = SiteDailyMetricsFactory()
        self.serializer = SiteDailyMetricsSerializer(
            instance=self.site_daily_metrics)

    @pytest.mark.skip(reason='Test not implemented yet')
    def test_time_zone(self):
        pass

    def test_has_fields(self):
        '''Verify the serialized data has the same keys and values as the model

        Django 2.0 has a convenient method, 'Cast' that will simplify converting
        values:
        https://docs.djangoproject.com/en/2.0/ref/models/database-functions/#cast

        This means that we can retrieve the model instance values as a dict
        and do a simple ``assert self.serializer.data == queryset.values(...)``
        '''

        data = self.serializer.data

        # Hack: Check date and datetime values explicitly
        assert data['date_for'] == str(self.site_daily_metrics.date_for)
        assert dateutil_parse(data['created']) == self.site_daily_metrics.created
        assert dateutil_parse(data['modified']) == self.site_daily_metrics.modified

        for field_name in (self.expected_results_keys - self.date_fields):
            assert data[field_name] == getattr(self.site_daily_metrics,field_name)
