"""Tests Figures GradesCache model

"""

import datetime
import pytest

from figures.models import LearnerCourseGradeMetrics

from tests.factories import CourseEnrollmentFactory


@pytest.mark.django_db
class TestLearnerCourseGradeMetrics(object):
    """Unit tests for figures.models.LearnerCourseGradeMetrics model

    Initially performing basic sanity checks for code coverage

    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
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
