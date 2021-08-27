"""Tests the figures.backfill module
"""
from __future__ import absolute_import
from datetime import datetime
import pytest
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
from six.moves import range
from six.moves import zip

from django.db import connection
from django.utils.timezone import utc

from figures.backfill import backfill_monthly_metrics_for_site
from figures.models import SiteMonthlyMetrics
from tests.factories import (
    CourseOverviewFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
    StudentModuleFactory,
    SiteFactory)
from tests.helpers import organizations_support_sites


if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory


@pytest.fixture
@pytest.mark.django_db
def backfill_test_data(db):
    """
    TODO: make counts different for each course per month
    """
    months_back = 6
    sm_per_month = [10+i for i in range(months_back+1)]
    site = SiteFactory()
    now = datetime.utcnow().replace(tzinfo=utc)

    first_month = now - relativedelta(months=months_back)
    last_month = now - relativedelta(months=1)
    course_overviews = [CourseOverviewFactory() for i in range(1)]
    count_check = []
    sm = []
    for i, dt in enumerate(rrule(freq=MONTHLY, dtstart=first_month, until=last_month)):
        for co in course_overviews:
            sm_count = sm_per_month[i]
            month_sm = [StudentModuleFactory(course_id=co.id,
                                             created=dt,
                                             modified=dt) for i in range(sm_count)]
            sm += month_sm
        count_check.append(dict(month=dt, month_sm=month_sm, sm_count=sm_count))
    if organizations_support_sites():
        org = OrganizationFactory(sites=[site])
        for co in course_overviews:
            OrganizationCourseFactory(organization=org, course_id=str(co.id))
        for rec in sm:
            UserOrganizationMappingFactory(user=rec.student,
                                           organization=org)
    else:
        org = OrganizationFactory()

    return dict(
        site=site,
        organization=org,
        course_overview=course_overviews,
        student_modules=sm,
        first_month=first_month,
        now=now,
        months_back=months_back,
        sm_per_month=sm_per_month,
        count_check=count_check
    )


def patched__get_fill_month_raw_sql_for_month(site_ids, month_for):
    """Get SQL statement for fill_month use_raw_sql option... that works with SQLite in test.
    """
    if (connection.vendor == 'sqlite'):
        month = str(month_for.month).zfill(2)
        year = month_for.year
        return """\
        SELECT COUNT(DISTINCT student_id) from courseware_studentmodule
        where id in {}
        and strftime('%m', datetime(modified)) = '{}'
        and strftime('%Y', datetime(modified)) = '{}'
        """.format(site_ids, month, year)


@pytest.mark.freeze_time('2019-09-01 12:00:00')
@pytest.mark.parametrize('use_raw_sql', (True, False))
def test_backfill_monthly_metrics_for_site(monkeypatch, backfill_test_data, use_raw_sql):
    """Simple coverage and data validation check for the function under test

    Example backfilled results
        [(<SiteMonthlyMetrics: id:1, month_for:2019-09-01, site:site-0.example.com>,
          True),
         (<SiteMonthlyMetrics: id:2, month_for:2019-10-01, site:site-0.example.com>,
          True),
         (<SiteMonthlyMetrics: id:3, month_for:2019-11-01, site:site-0.example.com>,
          True),
         (<SiteMonthlyMetrics: id:4, month_for:2019-12-01, site:site-0.example.com>,
          True),
         (<SiteMonthlyMetrics: id:5, month_for:2020-01-01, site:site-0.example.com>,
          True),
         (<SiteMonthlyMetrics: id:6, month_for:2020-02-01, site:site-0.example.com>,
          True),
         (<SiteMonthlyMetrics: id:7, month_for:2020-03-01, site:site-0.example.com>,
          True),
         (<SiteMonthlyMetrics: id:8, month_for:2020-04-01, site:site-0.example.com>,
          True)]

    TODO: Update test data and test to have the created and modified dates different
    and make sure that `modified` dates are used in the production code and not
    `created` dates
    """
    # monkeypatch the function which produces the raw sql w/one will work in test
    monkeypatch.setattr(
        "figures.pipeline.site_monthly_metrics._get_fill_month_raw_sql_for_month",
        patched__get_fill_month_raw_sql_for_month
    )

    site = backfill_test_data['site']
    count_check = backfill_test_data['count_check']
    assert not SiteMonthlyMetrics.objects.count()
    backfilled = backfill_monthly_metrics_for_site(site=site, overwrite=True, use_raw_sql=use_raw_sql)
    assert len(backfilled) == backfill_test_data['months_back']
    assert len(backfilled) == SiteMonthlyMetrics.objects.count()
    assert len(backfilled) == len(count_check)
    for rec, check_rec in zip(backfilled, count_check):
        assert rec['obj'].active_user_count == check_rec['sm_count']
        assert rec['obj'].month_for.year == check_rec['month'].year
        assert rec['obj'].month_for.month == check_rec['month'].month
