"""

# Background

Figures originally calculated completions as the certificates generated


As of mid 2020, we are reworking metrics so that course completsions are based
off of gradable sections likely followed by using or adapting the completion
aggregator

We need to rename our current "completion" to indicate certificates and not
completsions

However, Figures UI and API still have the "completions" label for certificates


# This Test Module

This test module tests certificate metrics. If you read "completions" in this
test module, think "certificates" until we do our relabelling

"""

import pytest
from datetime import date
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from figures.helpers import days_in_month
from figures.metrics import get_total_course_completions_for_time_period
from figures.models import CourseDailyMetrics

from tests.factories import (
    CourseDailyMetricsFactory,
    CourseOverviewFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
    SiteFactory
)

from tests.helpers import organizations_support_sites


@pytest.fixture
@pytest.mark.django_db
def cdm_test_data(db, settings):
    """Build CourseDailyMetrics data to test certificate counts
    """
    our_site = SiteFactory()
    mock_today = date(year=2020, month=6, day=7)
    last_month = mock_today - relativedelta(months=1)
    courses = [CourseOverviewFactory() for i in range(2)]
    # Create data for previous month. Just need one record
    # purpose is to make sure it is not included in our production code request
    prev_month_cdm = [CourseDailyMetrics(site=our_site,
                                         course_id=str(courses[0].id),
                                         date_for=last_month)]

    # Create data for our current month
    curr_month_cdm = []
    cdm_data = [
        dict(day=1, course_id=str(courses[0].id), num_learners_completed=1),
        dict(day=6, course_id=str(courses[0].id), num_learners_completed=10),
        dict(day=1, course_id=str(courses[1].id), num_learners_completed=2),
        dict(day=6, course_id=str(courses[1].id), num_learners_completed=20),
    ]

    expected_cert_count = 30
    for rec in cdm_data:
        date_for = date(year=mock_today.year, month=mock_today.month, day=rec['day'])
        cdm = CourseDailyMetricsFactory(
            site=our_site,
            course_id=rec['course_id'],
            date_for=date_for,
            num_learners_completed=rec['num_learners_completed'])
        curr_month_cdm.append(cdm)

    if organizations_support_sites():
        settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        our_org = OrganizationFactory(sites=[our_site])
        for course in courses:
            OrganizationCourseFactory(organization=our_org,
                                      course_id=str(course.id))
    return dict(
        mock_today=mock_today,
        our_site=our_site,
        courses=courses,
        prev_month_cdm=prev_month_cdm,
        curr_month_cdm=curr_month_cdm,
        expected_cert_count=expected_cert_count,
    )


def test_certificate_metrics(cdm_test_data):
    date_for = cdm_test_data['mock_today']
    site = cdm_test_data['our_site']
    expected_cert_count = cdm_test_data['expected_cert_count']
    freezer = freeze_time(date_for)
    freezer.start()

    start_date = date(year=date_for.year, month=date_for.month, day=1)
    end_date = date(year=date_for.year,
                    month=date_for.month,
                    day=days_in_month(date_for))

    count = get_total_course_completions_for_time_period(site=site,
                                                         start_date=start_date,
                                                         end_date=end_date)
    freezer.stop()
    assert count == expected_cert_count
