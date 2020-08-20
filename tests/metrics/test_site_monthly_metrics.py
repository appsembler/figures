"""
"""

from __future__ import absolute_import
from datetime import date
from freezegun import freeze_time

from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta

import pytest

from figures.metrics import get_site_mau_history_metrics
from figures.models import SiteMonthlyMetrics

from tests.factories import (
    SiteDailyMetricsFactory,
    SiteMonthlyMetricsFactory,
    SiteFactory,
)


@pytest.mark.django_db
def test_get_site_mau_history_metrics_basic(db, monkeypatch):
    """Simple data, skipping doing a fixture for now

    Expected data:
        {'current_month': 12,
         'history': [{'period': '2019/12', 'value': 6},
                     {'period': '2020/01', 'value': 7},
                     {'period': '2020/02', 'value': 8},
                     {'period': '2020/03', 'value': 9},
                     {'period': '2020/04', 'value': 10},
                     {'period': '2020/05', 'value': 11},
                     {'period': '2020/06', 'value': 12}]}

    TODO: We want to revisit both this test and the function under test
    """
    all_months_back = 12
    months_back = 6
    mock_today = date(year=2020, month=6, day=1)
    last_month = mock_today - relativedelta(months=1)
    freezer = freeze_time(mock_today)
    freezer.start()

    start_month = mock_today - relativedelta(months=all_months_back)
    smm = []
    our_site = SiteFactory()
    other_site = SiteFactory()

    for site in [our_site, other_site]:
        for counter, dt in enumerate(rrule(freq=MONTHLY,
                                           dtstart=start_month,
                                           until=last_month)):
            month_for = date(year=dt.year, month=dt.month, day=1)
            smm.append(SiteMonthlyMetricsFactory(site=site,
                                                 month_for=month_for,
                                                 active_user_count=counter))

    current_month_active = 42
    SiteDailyMetricsFactory(site=our_site,
                            date_for=mock_today - relativedelta(day=2),
                            mau=current_month_active)

    data = get_site_mau_history_metrics(site=our_site, months_back=months_back)

    freezer.stop()

    assert data['current_month'] == current_month_active
    for rec in data['history'][:-1]:
        year, month = [int(val) for val in rec['period'].split('/')]
        month_for = date(year=year, month=month, day=1)
        obj = SiteMonthlyMetrics.objects.get(site=our_site, month_for=month_for)
        assert obj.active_user_count == rec['value']
        assert obj.site == our_site
