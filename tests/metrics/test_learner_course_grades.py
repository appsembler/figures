
import pytest


from figures.metrics import LearnerCourseGrades

from tests.factories import CourseEnrollmentFactory

@pytest.mark.django_db
class TestLearnerCourseGrades(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        pass

    def test_get_progress(self):
        expected_response = dict(count=0, possible=0, earned=0)
        course_enrollment = CourseEnrollmentFactory()
        lcg = LearnerCourseGrades(
            user_id=course_enrollment.user.id,
            course_id=course_enrollment.course_id)

        assert lcg
        progress = lcg.progress()
        assert set(progress.keys()) == set(expected_response.keys())
