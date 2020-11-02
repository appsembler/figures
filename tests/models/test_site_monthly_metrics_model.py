"""Tests SiteMonthlyMetrics model

"""

from __future__ import absolute_import
from datetime import date
import pytest
from figures.models import SiteMonthlyMetrics

from tests.factories import (
    SiteFactory
)


@pytest.mark.django_db
class TestSiteDailyMetrics(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = SiteFactory()

    def test_create(self):

        assert not SiteMonthlyMetrics.objects.count()
        year = 2020
        month = 4

        rec = dict(
            site=self.site,
            year=year,
            month=month,
            active_user_count=42,
        )
        expected_month_for = date(year=year, month=month, day=1)
        metrics, created = SiteMonthlyMetrics.add_month(**rec)
        assert metrics and created
        assert metrics.month_for == expected_month_for
        assert metrics.active_user_count == rec['active_user_count']
