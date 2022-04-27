"""Test the module level functions in figures.pipeline.site_daily_metrics

First
"""
from __future__ import absolute_import
import pytest

from django.utils.timezone import utc
from faker import Faker

from figures.helpers import days_from
from figures.pipeline.site_daily_metrics import (
    get_course_ids_enrolled_on_or_before
)

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    SiteFactory,
    )


fake = Faker()


@pytest.mark.django_db
class TestGetCoursesEnrolledOnOrBefore(object):
    """Tests the `get_course_ids_enrolled_on_or_before` function
    """
    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        # self.course_overview = CourseOverviewFactory()
        self.site = SiteFactory()
        # Try for any datetime with `fake.date_time()` as the code we test here
        # should be agnostic to "any when". If it turns up to fail, then we
        # need to inspect the code as to why
        self.date_for = fake.date_time(tzinfo=utc)
        self.site_course_ids = 'figures.pipeline.site_daily_metrics.site_course_ids',

    def test_with_no_courses(self, monkeypatch):
        monkeypatch.setattr('figures.pipeline.site_daily_metrics.site_course_ids',
                            lambda site: [])
        found_cids = get_course_ids_enrolled_on_or_before(self.site,
                                                          self.date_for)
        assert found_cids == []

    def test_with_no_enrollments(self, monkeypatch):
        course_overview = CourseOverviewFactory()
        monkeypatch.setattr('figures.pipeline.site_daily_metrics.site_course_ids',
                            lambda site: [str(course_overview.id)])
        found_cids = get_course_ids_enrolled_on_or_before(self.site,
                                                          self.date_for)
        assert found_cids == []

    def test_mix(self, monkeypatch):
        """
        This should cover our cases. We shouldn't need
        `test_all_before` or `test_all_after`
        """

        # Construct enrollments on days before date_for
        ce_before = [
            CourseEnrollmentFactory(created=days_from(self.date_for, days))
            for days in range(-2, 0)
        ]
        ce_before_cids = [str(ce.course_id) for ce in ce_before]

        # Construct enrollments on date for
        ce_date_for = [CourseEnrollmentFactory(created=self.date_for)]
        ce_date_for_cids = [str(ce.course_id) for ce in ce_date_for]

        # Construct enrollments on days after date_for
        ce_after = [CourseEnrollmentFactory(created=days_from(self.date_for, days))
                    for days in range(1, 3)]
        ce_after_cids = [str(ce.course_id) for ce in ce_after]

        # adaptable checks to make sure we don't have duplicate course ids
        assert not set.intersection(set(ce_before_cids), set(ce_after_cids))
        assert not set.intersection(set(ce_before_cids), set(ce_date_for_cids))
        assert not set.intersection(set(ce_date_for_cids), set(ce_after_cids))

        all_cids = ce_before_cids + ce_date_for_cids + ce_after_cids
        monkeypatch.setattr('figures.pipeline.site_daily_metrics.site_course_ids',
                            lambda site: all_cids)
        monkeypatch.setattr('figures.course.get_site_for_course',
                            lambda course_id: self.site)
        found_cids = get_course_ids_enrolled_on_or_before(self.site,
                                                          self.date_for)
        assert set(found_cids) == set(ce_before_cids + ce_date_for_cids)
