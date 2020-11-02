'''Tests Figures SiteDailyMetrics model

'''

from __future__ import absolute_import
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

    def test_create(self):
        '''Sanity check we can create the SiteDailyMetrics model

        Create a second instance the way we'll do it in the production code.
        Assert this is correct
        '''

        rec = dict(
            site=Site.objects.first(),
            date_for=datetime.date(2018, 2, 2),
            defaults=dict(
                cumulative_active_user_count=11,
                total_user_count=1,
                course_count=1,
                total_enrollment_count=1,
                mau=1,
            ),
        )
        site_metrics, created = SiteDailyMetrics.objects.get_or_create(**rec)
        assert created and site_metrics

    def test_multiple_sites(self):
        """
        Tests expected SiteDailyMetrics behavior for working with a Site
        """
        assert Site.objects.count() == 1
        default_site = Site.objects.first()
        rec = dict(
            site=Site.objects.first(),
            date_for=datetime.date(2018, 2, 2),
            cumulative_active_user_count=11,
            total_user_count=1,
            course_count=1,
            total_enrollment_count=1,
            mau=1,
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

    def test_latest_previous_record(self):
        site = SiteFactory()

        # Create a set of records with non-continuous dates
        dates = [
            datetime.date(2019, 10, 1),
            datetime.date(2019, 10, 2),
            datetime.date(2019, 10, 5),
            datetime.date(2019, 10, 29),
            datetime.date(2019, 11, 3),
        ]
        for rec_date in dates:
            SiteDailyMetricsFactory(site=site, date_for=rec_date)

        rec = SiteDailyMetrics.latest_previous_record(site=site)
        assert rec.date_for == dates[-1]

        rec2 = SiteDailyMetrics.latest_previous_record(site=site,
                                                       date_for=dates[-1])
        assert rec2.date_for == dates[-2]

        rec3 = SiteDailyMetrics.latest_previous_record(site=site,
                                                       date_for=dates[0])
        assert not rec3
