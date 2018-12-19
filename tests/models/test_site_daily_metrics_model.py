'''Tests Figures SiteDailyMetrics model

'''

import datetime
import pytest

from django.contrib.sites.models import Site
from django.db.utils import IntegrityError

from figures.models import SiteDailyMetrics

from tests.factories import SiteFactory, SiteDailyMetricsFactory


@pytest.mark.django_db
class TestSiteDailyMetrics(object):
    '''Tests the SiteDailyMetrics model

    Focus on testing SiteDailyMetrics methods and fields
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        '''Placeholder for test setup

        '''

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

    def test_site(self):
        """
        Tests expected SiteDailyMetrics behavior for working with a Site
        """
        assert Site.objects.count() == 1
        default_site = Site.objects.first()
        rec = dict(
            date_for=datetime.date(2018, 02, 02),
            cumulative_active_user_count=11,
            total_user_count=1,
            course_count=1,
            total_enrollment_count=1
        )
        obj = SiteDailyMetrics.objects.create(**rec)
        assert obj.site == default_site

        alpha_site = SiteFactory(domain='alpha.example.com', name='Alpha')
        assert Site.objects.count() == 2
        rec['site'] = alpha_site
        obj2 = SiteDailyMetrics.objects.create(**rec)
        assert obj2.site == alpha_site

        # Test cascade delete
        assert SiteDailyMetrics.objects.count() == 2
        alpha_site.delete()
        assert SiteDailyMetrics.objects.count() == 1
        # Verify we deleted the correct metrics object
        assert obj == SiteDailyMetrics.objects.first()
