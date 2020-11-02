"""Tests pipeline loaders for loaders not defined in metrics specific loader
modules: course_daily_metrics, site_daily_metrics

"""

from __future__ import absolute_import
import datetime
import pytest

from django.contrib.sites.models import Site

from figures.models import LearnerCourseGradeMetrics
import figures.pipeline.loaders

from tests.factories import CourseEnrollmentFactory


@pytest.mark.django_db
class TestSaveLearnerCourseGrades(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = Site.objects.first()
        self.date_for = datetime.date(2018, 2, 2)
        self.course_enrollment = CourseEnrollmentFactory()
        self.user = self.course_enrollment.user

    def test_save_new_with_good_data(self):
        details = dict(
            points_possible=10.0,
            points_earned=5.0,
            sections_worked=15,
            count=20,
            )
        assert LearnerCourseGradeMetrics.objects.count() == 0

        obj, created = figures.pipeline.loaders.save_learner_course_grades(
            site=self.site,
            date_for=self.date_for,
            course_enrollment=self.course_enrollment,
            course_progress_details=details)
        assert LearnerCourseGradeMetrics.objects.count() == 1
        assert obj.site == self.site
        assert obj.course_id == str(self.course_enrollment.course_id)
        assert obj.points_possible == details['points_possible']
        assert obj.points_earned == details['points_earned']
        assert obj.sections_worked == details['sections_worked']
        assert obj.sections_possible == details['count']
