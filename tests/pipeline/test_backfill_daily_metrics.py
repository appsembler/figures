"""Tests figures.pipeline.backfill historic daily metrics backfill functionality

These functions are tested when `backfill_daily_metrics_for_site_and_date` is called:

* `get_courses_first_enrollment_timestamps`
* `courses_enrolled_on_or_before`
"""

from __future__ import absolute_import
import pytest

try:
    from unittest import mock
except ImportError:
    # for Python 2.7
    import mock

from figures.helpers import as_date, as_datetime
from figures.models import CourseDailyMetrics, SiteDailyMetrics
from figures.pipeline.backfill import (

    backfill_daily_metrics_for_site_and_date
)

from tests.factories import (
    CourseOverviewFactory,
    CourseEnrollmentFactory,
    SiteFactory,
)


@pytest.mark.django_db
class TestBackfillDailyMetricsForSiteAndDate(object):

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        self.site = SiteFactory()

    def test_happy_case(self, monkeypatch):
        """Make sure it works when everything is good

        This test expects two courses to be processed and one course skipped
        """
        date_for = as_date('2022-01-01')
        course_overviews = [CourseOverviewFactory(),
                            CourseOverviewFactory(),
                            CourseOverviewFactory()]

        # Enrollments for the first course
        # Both enrollments created before the "date_for" date
        CourseEnrollmentFactory(course_id=course_overviews[0].id,
                                created=as_datetime('2020-05-15'))
        CourseEnrollmentFactory(course_id=course_overviews[0].id,
                                created=as_datetime('2020-06-15'))

        # Enrollments for the second course
        # One enrollment created before the "date_for" date and one after
        CourseEnrollmentFactory(course_id=course_overviews[1].id,
                                created=as_datetime('2021-05-15'))
        # This one shouldn't show up in the CDM record
        CourseEnrollmentFactory(course_id=course_overviews[1].id,
                                created=as_datetime('2022-02-15'))

        # Enrollment for the third course
        # This enrollment created after the "date_for" date
        # A CDM record should not be created for this course
        CourseEnrollmentFactory(course_id=course_overviews[2].id,
                                created=as_datetime('2022-02-15'))

        assert CourseDailyMetrics.objects.count() == 0
        assert SiteDailyMetrics.objects.count() == 0

        open_mock = mock.mock_open()

        monkeypatch.setattr('figures.pipeline.backfill.get_course_keys_for_site',
                            lambda site: [obj.id for obj in course_overviews])
        monkeypatch.setattr('figures.pipeline.course_daily_metrics.figures.sites.get_site_for_course',
                            lambda course_id: self.site)
        with mock.patch('figures.pipeline.backfill.open', open_mock):
            results = backfill_daily_metrics_for_site_and_date(
                site=self.site,
                date_for=date_for)

        # If this fails, check the write mode
        open_mock.assert_called_with(results['logfile'], 'a', encoding='utf-8')

        # For now, we're just basic that records were created for the expected
        # courses and site. Metrics values are tested in other tests
        found_course_ids = CourseDailyMetrics.objects.values_list('course_id', flat=True)
        expected_course_ids = [str(obj.id) for obj in course_overviews[:2]]
        assert set(found_course_ids) == set(expected_course_ids)
        assert SiteDailyMetrics.objects.count() == 1
        assert SiteDailyMetrics.objects.first().site == self.site

    def test_empty_case(self, monkeypatch):
        """Make sure it works when everything is good

        This test expects two courses to be processed and one course skipped
        """
        date_for = as_date('2022-01-01')
        course_overviews = [CourseOverviewFactory(),
                            CourseOverviewFactory(),
                            CourseOverviewFactory()]

        assert CourseDailyMetrics.objects.count() == 0
        assert SiteDailyMetrics.objects.count() == 0

        open_mock = mock.mock_open()

        monkeypatch.setattr('figures.pipeline.backfill.get_course_keys_for_site',
                            lambda site: [obj.id for obj in course_overviews])

        with mock.patch('figures.pipeline.backfill.open', open_mock):
            results = backfill_daily_metrics_for_site_and_date(
                site=self.site,
                date_for=date_for)

        open_mock.assert_called_with(results['logfile'], 'a', encoding='utf-8')

        # For now, we're just basic that records were created for the expected
        # courses and site. Metrics values are tested in other tests
        assert CourseDailyMetrics.objects.count() == 0
        assert SiteDailyMetrics.objects.count() == 1
        assert SiteDailyMetrics.objects.first().site == self.site
