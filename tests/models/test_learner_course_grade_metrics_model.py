'''Tests Figures GradesCache model

'''

import datetime
import pytest

from figures.models import LearnerCourseGradeMetrics

from tests.factories import CourseEnrollmentFactory


@pytest.mark.django_db
class TestLearnerCourseGradeMetrics(object):
    """

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
