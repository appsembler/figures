"""Tests for Course Monthly Metrics data collection
"""

from __future__ import absolute_import
import pytest
from django.contrib.auth import get_user_model

from figures.metrics import (
    get_course_mau_history_metrics,
    get_month_course_metrics,
)

from tests.factories import (
    CourseOverviewFactory,
    SiteFactory,
    UserFactory,
)


@pytest.mark.django_db
def test_get_course_mau_history_metrics(monkeypatch):
    """Initially basic test for coverage and structure of return data

    TODO: Create generalized "history structure check" so we can use the single
    test to check all historical metrics data
    {
        'current_month': 1,
        'history': [
            {'period': '2019/10', 'value': 1},
            {'period': '2019/11', 'value': 1},
            {'period': '2019/12', 'value': 1},
            {'period': '2020/01', 'value': 1},
            {'period': '2020/02', 'value': 1},
            {'period': '2020/03', 'value': 1},
            {'period': '2020/04', 'value': 1}
        ]
    }
    """
    UserFactory()

    def mock_get_mau_from_site_course(**_kwargs):
        return get_user_model().objects.all()

    monkeypatch.setattr('figures.metrics.get_mau_from_site_course',
                        mock_get_mau_from_site_course)
    site = SiteFactory()
    course_overview = CourseOverviewFactory()
    date_for = '2020/4/1'
    months_back = 6

    # test with course id as a `CourseKey` instance
    data = get_course_mau_history_metrics(
        site=site,
        course_id=course_overview.id,
        date_for=date_for,
        months_back=months_back)
    assert set(data.keys()) == set(['current_month', 'history'])

    # test with course id as a string
    data = get_course_mau_history_metrics(
        site=site,
        course_id=str(course_overview.id),
        date_for=date_for,
        months_back=months_back)
    assert set(data.keys()) == set(['current_month', 'history'])


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

    # Set up the mocks that our function under test will call
    monkeypatch.setattr('figures.metrics.get_mau_from_site_course',
                        mock_get_mau_from_site_course)
    monkeypatch.setattr('figures.metrics.get_course_enrolled_users_for_time_period',
                        lambda **_kwargs: expected_data['course_enrollments'])
    monkeypatch.setattr('figures.metrics.get_course_num_learners_completed_for_time_period',
                        lambda **_kwargs: expected_data['num_learners_completed'])
    monkeypatch.setattr('figures.metrics.get_course_average_days_to_complete_for_time_period',
                        lambda **_kwargs: expected_data['avg_days_to_complete'])
    monkeypatch.setattr('figures.metrics.get_course_average_progress_for_time_period',
                        lambda **_kwargs: expected_data['avg_progress'])

    data = get_month_course_metrics(site=site,
                                    course_id=course_id,
                                    month_for=expected_data['month_for'])

    assert data == expected_data
