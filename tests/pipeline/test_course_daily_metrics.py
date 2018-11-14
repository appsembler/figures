"""Tests the pipeline to extract data and populate the CourseDailyMetrics model

"""

import datetime
import mock
import pytest

from django.core.exceptions import PermissionDenied

from student.models import CourseEnrollment, CourseAccessRole

from figures.helpers import as_datetime, next_day, prev_day
from figures.models import PipelineError
from figures.pipeline import course_daily_metrics as pipeline_cdm

from tests.factories import (
    CourseAccessRoleFactory,
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    GeneratedCertificateFactory,
    StudentModuleFactory,
)


@pytest.mark.django_db
class TestGetCourseEnrollments(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.today = datetime.date(2018, 6, 1)
        self.course_overviews = [CourseOverviewFactory() for i in range(1, 3)]
        self.course_enrollments = []
        for co in self.course_overviews:
            self.course_enrollments.extend(
                [CourseEnrollmentFactory(course_id=co.id) for i in range(1, 3)])

    def test_get_all_course_enrollments(self):
        """
        Sanity check test that we have all the course enrollments in
        self.course_enrollments
        """
        assert len(self.course_enrollments) == CourseEnrollment.objects.count()

    def test_get_course_enrollments_for_course(self):
        course_id = self.course_overviews[0].id
        expected_ce = CourseEnrollment.objects.filter(
            course_id=course_id,
            created__lt=as_datetime(
                next_day(self.today))).values_list('id', flat=True)
        results_ce = pipeline_cdm.get_course_enrollments(
            course_id=course_id,
            date_for=self.today).values_list('id', flat=True)
        assert set(results_ce) == set(expected_ce)


@pytest.mark.django_db
class TestCourseDailyMetricsPipelineFunctions(object):
    """
    Initial implementation is focused on setting a baseline and providing code
    coverage. It also only tests with the date_for of 'now' and creates test
    data with dates in the past.

    We're also setting up a bunch of data and strictly only some are needed for
    each method, so it would be more efficient to break this out into seperate
    test classes

    TODO: Update test data for a series of dates and test 'date_for' for a date
    in the past where test data will contain data before on and after the
    date we'll pass as the 'date_for' parameter
    """
    COURSE_ROLES = ['ccx_coach', 'instructor', 'staff']

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.today = datetime.date(2018, 6, 1)
        self.course_overview = CourseOverviewFactory()
        self.course_enrollments = [CourseEnrollmentFactory(
            course_id=self.course_overview.id) for i in range(4)]

        self.course_access_roles = [CourseAccessRoleFactory(
            user=self.course_enrollments[i].user,
            course_id=self.course_enrollments[i].course_id,
            role=role,
            ) for i, role in enumerate(self.COURSE_ROLES)]

        # create student modules for yesterday and today
        for day in [prev_day(self.today), self.today]:
            self.student_modules = [StudentModuleFactory(
                course_id=ce.course_id,
                student=ce.user,
                created=ce.created,
                modified=as_datetime(day)
                ) for ce in self.course_enrollments]

        self.cert_days_to_complete = [10, 20, 30]
        self.expected_avg_cert_days_to_complete = 20
        self.generated_certificates = [
            GeneratedCertificateFactory(
                user=self.course_enrollments[i].user,
                course_id=self.course_enrollments[i].course_id,
                created_date=(
                    self.course_enrollments[i].created + datetime.timedelta(
                        days=days)
                    ),
            ) for i, days in enumerate(self.cert_days_to_complete)]

    def test_get_num_enrolled_in_exclude_admins(self):
        """

        """

        # Get the number of course enrollments
        ce_count = CourseEnrollment.objects.filter(
            course_id=self.course_overview.id).count()
        # Get course admins (non-students)
        ce_non_students = CourseAccessRole.objects.filter(
            course_id=self.course_overview.id).count()

        expected_count = ce_count - ce_non_students
        assert ce_count > 0 and ce_non_students > 0 and expected_count > 0, 'say something'

        actual_count = pipeline_cdm.get_num_enrolled_in_exclude_admins(
            course_id=self.course_overview.id, date_for=self.today)

        assert actual_count == expected_count

        actual_count = pipeline_cdm.get_num_enrolled_in_exclude_admins(
            course_id=str(self.course_overview.id), date_for=self.today)
        assert actual_count == expected_count

    def test_get_active_learner_ids_today(self):
        """

        TODO: in the setup, add student module records modified in the past and
        add filtering to the expected_count here
        """
        recs = pipeline_cdm.get_active_learner_ids_today(
            course_id=self.course_overview.id, date_for=self.today)
        assert recs.count() == len(self.course_enrollments)

    def test_get_average_progress(self):
        """
        [John] This test needs work. The function it is testing needs work too
        for testability. We don't want to reproduce the function's behavior, we
        just want to be able to set up the source data with expected output and
        go.
        """
        course_enrollments = CourseEnrollment.objects.filter(
            course_id=self.course_overview.id)

        actual = pipeline_cdm.get_average_progress(
            course_id=self.course_overview.id,
            date_for=self.today,
            course_enrollments=course_enrollments
            )

        # See tests/mocks/lms/djangoapps/grades/new/course_grade.py for
        # the source subsection grades that

        # TODO: make the mock data more configurable so we don't have to
        # hardcode the expected value
        assert actual == 0.5

    @mock.patch(
        'figures.metrics.LearnerCourseGrades.course_progress',
        side_effect=PermissionDenied('mock-failure')
    )
    def test_get_average_progress_error(self, mock_lcg):
        assert PipelineError.objects.count() == 0
        course_enrollments = CourseEnrollment.objects.filter(
            course_id=self.course_overview.id)

        results = pipeline_cdm.get_average_progress(
                course_id=self.course_overview.id,
                date_for=self.today,
                course_enrollments=course_enrollments
                )
        assert results == pytest.approx(0.0)
        assert PipelineError.objects.count() == course_enrollments.count()

    def test_get_days_to_complete(self):
        expected = dict(
            days=self.cert_days_to_complete,
            errors=[])

        actual = pipeline_cdm.get_days_to_complete(
            course_id=self.course_overview.id,
            date_for=self.today)

        assert actual == expected

    def test_calc_average_days_to_complete(self):
        actual = pipeline_cdm.calc_average_days_to_complete(
            self.cert_days_to_complete)

        assert actual == self.expected_avg_cert_days_to_complete

    def test_get_average_days_to_complete(self):
        actual = pipeline_cdm.get_average_days_to_complete(
            course_id=self.course_overview.id,
            date_for=self.today)
        assert actual == self.expected_avg_cert_days_to_complete

    def test_get_num_learners_completed(self):
        actual = pipeline_cdm.get_num_learners_completed(
            course_id=self.course_overview.id,
            date_for=self.today)
        assert actual == len(self.generated_certificates)


@pytest.mark.django_db
class TestCourseDailyMetricsExtractor(object):
    """
    Provides minimal checking that CourseDailyMetricsExtractor works

    * Verifies that we can create an instance of the class
    * Verifies that we can call the extract method
    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.course_enrollments = [CourseEnrollmentFactory() for i in range(1, 5)]
        self.student_module = StudentModuleFactory()

    def test_extract(self):
        course_id = self.course_enrollments[0].course_id
        results = pipeline_cdm.CourseDailyMetricsExtractor().extract(course_id)
        assert results


@pytest.mark.django_db
class TestCourseDailyMetricsLoader(object):
    """Provides minimal checking that CourseDailyMetricsLoader works
    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.course_enrollments = [CourseEnrollmentFactory() for i in range(1, 5)]
        self.student_module = StudentModuleFactory()

    def test_load(self):
        course_id = self.course_enrollments[0].course_id
        results = pipeline_cdm.CourseDailyMetricsLoader(course_id).load()
        assert results
