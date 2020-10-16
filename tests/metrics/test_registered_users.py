"""Tests for registered user metrics

This module tests metrics functionality in `figures.metrics` that work with
the "registered user" metric

The registered user metric provides the count of how many users have registered
for a given site for a time range

TODO: Provide details here
* Figures UI registered users on a site
* The pipeline, storage, API retrieval, and any derivative metrics

# Developer Note

* Initially, we have basic tests for coverage

* We've just changed the metric from live User model `date_joined` queries to
  using stored data in `SiteDailyMetrics.total_user_count`
* We need to deploy quickly, so doing minimal testing to start


"""

from datetime import datetime
import pytest

from figures.metrics import get_total_site_users_for_time_period

from tests.factories import (
    SiteDailyMetricsFactory,
    SiteFactory,
)


@pytest.fixture
@pytest.mark.django_db
def sdm_test_data(db):
    """Quick-n-dirty test data construction

    Expected count is the highest 'total_user_count'
    """
    dates = [
        datetime(year=2020, month=3, day=15),
        datetime(year=2020, month=4, day=1),
        datetime(year=2020, month=4, day=15),
        datetime(year=2020, month=4, day=30),
        datetime(year=2020, month=5, day=1)
    ]

    our_date_range = [
        datetime(year=2020, month=4, day=1),
        datetime(year=2020, month=4, day=30),
    ]
    my_site = SiteFactory()
    other_site = SiteFactory()

    my_sdm = [
        # month before
        SiteDailyMetricsFactory(site=my_site,
                                date_for=dates[0],
                                total_user_count=10),
        # in our date range
        SiteDailyMetricsFactory(site=my_site,
                                date_for=dates[1],
                                total_user_count=20),
        SiteDailyMetricsFactory(site=my_site,
                                date_for=dates[2],
                                total_user_count=30),
        SiteDailyMetricsFactory(site=my_site,
                                date_for=dates[3],
                                total_user_count=25),
        # month after
        SiteDailyMetricsFactory(site=my_site,
                                date_for=dates[4],
                                total_user_count=500),
    ]
    # Create one SDM record for the other site in the month we query
    other_sdm = [
        SiteDailyMetricsFactory(site=other_site,
                                date_for=dates[2],
                                total_user_count=13)]
    return dict(
        our_date_range=our_date_range,
        my_site=my_site,
        other_site=other_site,
        my_sdm=my_sdm,
        other_sdm=other_sdm,
        expected_count=30,
    )


def test_get_total_site_users_for_month(sdm_test_data):
    """
    """
    my_site = sdm_test_data['my_site']
    start_date, end_date = sdm_test_data['our_date_range']
    count = get_total_site_users_for_time_period(
        site=my_site,
        start_date=start_date,
        end_date=end_date)
    assert count == sdm_test_data['expected_count']
