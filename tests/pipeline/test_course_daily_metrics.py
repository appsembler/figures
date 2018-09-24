'''

'''

import datetime
import pytest

from django.utils.timezone import utc

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from student.models import CourseEnrollment

# from figures.pipeline.course_daily_metrics import (
#     CourseDailyMetricsExtractor,
#     CourseDailyMetricsLoader,
# )

from figures.helpers import next_day
from figures.pipeline import course_daily_metrics as pipeline_cdm

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    StudentModuleFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestGetCourseEnrollments(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        '''

        '''
        #self.today = datetime.datetime.utcnow().replace(tzinfo=utc).date()
        self.today = datetime.datetime(2018,6,1).replace(tzinfo=utc).date()
        self.course_overviews = [CourseOverviewFactory() for i in range(1,3)]
        self.course_enrollments = []
        for co in self.course_overviews:
            self.course_enrollments.extend(
                [CourseEnrollmentFactory(course_id=co.id) for i in range(1,3)])

    def test_get_all_course_enrollments(self):
        '''
        Sanity check test that we have all the course enrollments in
        self.course_enrollments
        '''
        assert len(self.course_enrollments) == CourseEnrollment.objects.count()


    def test_get_course_enrollments_for_course(self):


        course_id = self.course_overviews[0].id
        expected_ce = CourseEnrollment.objects.filter(
            course_id=course_id,
            created__lt=next_day(self.today)).values_list('id', flat=True)
        results_ce = pipeline_cdm.get_course_enrollments(
            course_id=course_id,
            date_for=self.today).values_list('id', flat=True)

        assert set(results_ce) == set(expected_ce)


@pytest.mark.django_db
class TestCourseDailyMetricsPipelineFunctions(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.course_enrollments = [CourseEnrollmentFactory() for i in range(1,5)]
        self.student_module = StudentModuleFactory()


    def test_get_num_enrolled_in_exclude_admins(self):
        pass

    def test_get_active_learners_today(self):
        pass

    def test_get_average_progress(self):
        pass

    def test_get_days_to_complete(self):
        pass

    def test_calc_average_days_to_complete(self):
        pass

    def test_get_average_days_to_complete(self):
        pass

    def test_get_num_learners_completed(self):
        pass


@pytest.mark.django_db
class TestCourseDailyMetricsExtractor(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.course_enrollments = [CourseEnrollmentFactory() for i in range(1,5)]
        self.student_module = StudentModuleFactory()

    def test_extract(self):

        course_id = self.course_enrollments[0].course_id
        results = pipeline_cdm.CourseDailyMetricsExtractor().extract(course_id)
        assert results

