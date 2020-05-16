"""Tests Figures GradesCache model

"""

import datetime
import pytest

from django.contrib.sites.models import Site
from django.utils.timezone import utc

from figures.helpers import as_date
from figures.models import LearnerCourseGradeMetrics

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    LearnerCourseGradeMetricsFactory,
    UserFactory
)


@pytest.mark.django_db
def test_most_recent_with_data(db):
    """Make sure the query works with a couple of existing models

    We create two LearnerCourseGradeMetrics models and test that the function
    retrieves the newer one
    """
    user = UserFactory()
    first_date = as_date('2020-02-02')
    second_date = as_date('2020-04-01')
    course_overview = CourseOverviewFactory()
    older_lcgm = LearnerCourseGradeMetricsFactory(user=user,
                                                  course_id=str(course_overview.id),
                                                  date_for=first_date)
    newer_lcgm = LearnerCourseGradeMetricsFactory(user=user,
                                                  course_id=str(course_overview.id),
                                                  date_for=second_date)

    obj = LearnerCourseGradeMetrics.objects.most_recent_for_learner_course(
        user=user, course_id=course_overview.id)
    assert obj == newer_lcgm


@pytest.mark.django_db
def test_most_recent_with_empty_table(db):
    """Make sure the query works when there are no models to find
    
    Tests that the function returns None and does not fail when it cannot find
    any LearnerCourseGradeMetrics model instances
    """
    assert not LearnerCourseGradeMetrics.objects.count()
    user = UserFactory()
    course_overview = CourseOverviewFactory()
    obj = LearnerCourseGradeMetrics.objects.most_recent_for_learner_course(
        user=user, course_id=course_overview.id)
    assert not obj


@pytest.mark.django_db
class TestLearnerCourseGradeMetrics(object):
    """Unit tests for figures.models.LearnerCourseGradeMetrics model

    Initially performing basic sanity checks for code coverage

    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = Site.objects.first()
        self.date_for = datetime.date(2018, 2, 2)
        self.course_enrollment = CourseEnrollmentFactory()
        self.grade_data = dict(
            points_possible=10.0,
            points_earned=5.0,
            sections_worked=2,
            sections_possible=2
            )
        self.create_rec = self.grade_data.copy()
        self.create_rec.update(dict(
            site=self.site,
            date_for=self.date_for,
            user=self.course_enrollment.user,
            course_id=self.course_enrollment.course_id))

    def test_create(self):
        obj = LearnerCourseGradeMetrics(**self.create_rec)
        assert str(obj) == '{} {} {} {}'.format(
            None,
            self.create_rec['date_for'],
            self.create_rec['user'].username,
            self.create_rec['course_id'])

    def test_most_recent_for_learner_course_one_rec(self):
        rec = LearnerCourseGradeMetrics.objects.create(**self.create_rec)
        assert LearnerCourseGradeMetrics.objects.count() == 1
        obj = LearnerCourseGradeMetrics.objects.most_recent_for_learner_course(
            user=self.course_enrollment.user,
            course_id=str(self.course_enrollment.course_id))
        assert rec == obj

    def test_most_recent_for_learner_course_multiple_dates(self):
        assert LearnerCourseGradeMetrics.objects.count() == 0
        for date in [datetime.date(2018, 2, day) for day in range(1, 4)]:
            rec = self.create_rec.copy()
            last_day = date
            rec['date_for'] = date
            LearnerCourseGradeMetrics.objects.create(**rec)

        obj = LearnerCourseGradeMetrics.objects.most_recent_for_learner_course(
            user=self.course_enrollment.user,
            course_id=str(self.course_enrollment.course_id))
        assert last_day
        assert obj.date_for == last_day

    def test_progress_percent(self):
        expected = (self.grade_data['sections_worked'] /
                    self.grade_data['sections_possible'])
        obj = LearnerCourseGradeMetrics(**self.create_rec)
        assert obj.progress_percent == expected

    def test_progress_percent_zero_sections_possible(self):
        create_rec = self.create_rec.copy()
        create_rec['sections_possible'] = 0
        obj = LearnerCourseGradeMetrics(**create_rec)
        assert obj.progress_percent == 0.0

    def test_progress_details(self):
        obj = LearnerCourseGradeMetrics(**self.create_rec)
        assert obj.progress_details == self.grade_data
