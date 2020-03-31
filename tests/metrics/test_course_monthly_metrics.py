"""Tests for Course Monthly Metrics data collection
"""

import pytest
from django.contrib.auth import get_user_model

from figures.metrics import get_month_course_metrics

from tests.factories import (
    CourseOverviewFactory,
    SiteFactory,
    UserFactory,
)


@pytest.mark.django_db
def test_get_month_course_metrics(monkeypatch):

    site = SiteFactory()
    course_overview = CourseOverviewFactory()
    course_id = str(course_overview.id)
    [UserFactory(), UserFactory()]
    users_qs = get_user_model().objects.all().values_list('id')
    expected_data = dict(
        course_id=course_id,
        month_for='02/2020',
        active_users=users_qs.count(),
        course_enrollments=101,
        num_learners_completed=102,
        avg_days_to_complete=103,
        avg_progress=0.5,
    )

    def mock_get_mau_from_site_course(site, course_id, year, month):
        assert year
        return users_qs

    def mock_get_course_enrolled_users_for_time_period(**_kwargs):
        return expected_data['course_enrollments']

    def mock_get_course_num_learners_completed_for_time_period(**_kwargs):
        return expected_data['num_learners_completed']

    def mock_get_course_average_days_to_complete_for_time_period(**_kwargs):
        return expected_data['avg_days_to_complete']

    def mock_get_course_average_progress_for_time_period(**_kwargs):
        return expected_data['avg_progress']

    # Set up the mocks that our function under test will call
    monkeypatch.setattr('figures.metrics.get_mau_from_site_course',
                        mock_get_mau_from_site_course)
    monkeypatch.setattr('figures.metrics.get_course_enrolled_users_for_time_period',
                        mock_get_course_enrolled_users_for_time_period)
    monkeypatch.setattr('figures.metrics.get_course_num_learners_completed_for_time_period',
                        mock_get_course_num_learners_completed_for_time_period)
    monkeypatch.setattr('figures.metrics.get_course_average_days_to_complete_for_time_period',
                        mock_get_course_average_days_to_complete_for_time_period)
    monkeypatch.setattr('figures.metrics.get_course_average_progress_for_time_period',
                        mock_get_course_average_progress_for_time_period)

    data = get_month_course_metrics(site=site,
                                    course_id=course_id,
                                    month_for=expected_data['month_for'])
    assert not cmp(data, expected_data)
