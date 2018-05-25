'''Tests Figures SiteDailyMetrics model

'''

import datetime
import pytest

from django.db.utils import IntegrityError

from figures.models import SiteDailyMetrics

from tests.factories import SiteDailyMetricsFactory


@pytest.mark.django_db
class TestSiteDailyMetrics(object):
    '''Tests the SiteDailyMetrics model

    Focus on testing SiteDailyMetrics methods and fields
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        '''Placeholder for test setup

        '''
        self.site_daily_metrics = [
            SiteDailyMetricsFactory()
        ]

    def test_foo(self):
        '''
        Assert that SiteDailyMetricsFactory works by checking the object
        created in this class's ``setup`` method.

        '''
        assert SiteDailyMetrics.objects.count() == 1


    @pytest.mark.parametrize('rec', [
        dict(
            date_for=datetime.date(2018,02,02),
            defaults=dict(
                cumulative_active_user_count=11,
                total_user_count=1,
                course_count=1,
                total_enrollment_count=1
            ),
        ),
    ])
    def test_create(self, rec):
        '''Sanity check we can create the SiteDailyMetrics model

        Create a second instance the way we'll do it in the production code.
        Assert this is correct
        '''

        site_metrics, created = SiteDailyMetrics.objects.get_or_create(**rec)

        assert created and site_metrics

