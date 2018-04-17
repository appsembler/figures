'''
Test models declared in edX Figures
'''

import datetime
import pytest

from edx_figures.models import CourseDailyMetrics, SiteDailyMetrics

from .factories import (
    CourseDailyMetricsFactory,
    SiteDailyMetricsFactory,
    )


@pytest.mark.django_db
class TestCourseDailyMetrics(object):
    '''Unit tests for the CourseDailyMetrics model

    Focuses on testing CourseDailyMetrics fields and methods
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.course_daily_metrics = [
            CourseDailyMetricsFactory()
        ]

    @pytest.mark.parametrize('rec', [
        dict(
            date_for=datetime.date(2018, 02, 02),
            defaults=dict(
                enrollment_count=11,
                active_learners_today=1,
                average_progress=0.5,
                average_days_to_complete=5,
                num_learners_completed=10
            ),
        ),
    ])
    def test_create(self, rec):
        '''Sanity check we can create the SiteDailyMetrics model

        Create a second instance the way we'll do it in the production code.
        Assert this is correct
        '''

        metrics, created = CourseDailyMetrics.objects.get_or_create(**rec)

        assert created and metrics


@pytest.mark.django_db
class TestSiteDailyMetrics(object):
    '''Unit tests for  the SiteDailyMetrics model

    Focus on testing SiteDailyMetrics methods and fields
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        '''

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
