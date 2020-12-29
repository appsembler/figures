"""Tests the pipeline to extract data and populate the CourseDailyMetrics model

TODO: Update this test module to test multisite environments
"""

from __future__ import absolute_import
import datetime
import mock
import pytest

from django.core.exceptions import PermissionDenied, ValidationError

from figures.compat import CourseAccessRole, CourseEnrollment
from figures.helpers import as_datetime, next_day, prev_day
from figures.models import CourseDailyMetrics, PipelineError
from figures.pipeline import course_daily_metrics as pipeline_cdm
import figures.sites

from tests.factories import (
    CourseAccessRoleFactory,
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    GeneratedCertificateFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
    SiteFactory,
    StudentModuleFactory,
)

from tests.helpers import (
    organizations_support_sites,
    OPENEDX_RELEASE,
    GINKGO,
)
from six.moves import range


if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory


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

    def test_get_course_enrollments_for_course(self):
        course_id = self.course_overviews[0].id
        expected_ce = CourseEnrollment.objects.filter(
            course_id=course_id,
            created__lt=as_datetime(
                next_day(self.today))).values_list('id', flat=True)
        results_ce = pipeline_cdm.get_enrolled_in_exclude_admins(
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
        if OPENEDX_RELEASE == GINKGO:
            self.course_enrollments = [CourseEnrollmentFactory(
                course_id=self.course_overview.id) for i in range(4)]
        else:
            self.course_enrollments = [CourseEnrollmentFactory(
                course=self.course_overview) for i in range(4)]

        if organizations_support_sites():
            self.my_site = SiteFactory(domain='my-site.test')
            self.my_site_org = OrganizationFactory(sites=[self.my_site])
            OrganizationCourseFactory(organization=self.my_site_org,
                                      course_id=str(self.course_overview.id))
            for ce in self.course_enrollments:
                UserOrganizationMappingFactory(user=ce.user,
                                               organization=self.my_site_org)

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

    def test_get_enrolled_in_exclude_admins(self):

        # Get the total number of course enrollments for the course
        ce_count = CourseEnrollment.objects.filter(
            course_id=self.course_overview.id).count()
        # Get course admins (non-students) count for the course
        ce_non_students = CourseAccessRole.objects.filter(
            course_id=self.course_overview.id).count()

        expected_count = ce_count - ce_non_students
        assert ce_count > 0 and ce_non_students > 0 and expected_count > 0, 'say something'

        learners = pipeline_cdm.get_enrolled_in_exclude_admins(
            course_id=self.course_overview.id, date_for=self.today)

        assert learners.count() == expected_count

        learners = pipeline_cdm.get_enrolled_in_exclude_admins(
            course_id=str(self.course_overview.id), date_for=self.today)
        assert learners.count() == expected_count

    def test_get_active_learner_ids_today(self):
        """

        TODO: in the setup, add student module records modified in the past and
        add filtering to the expected_count here
        """
        recs = pipeline_cdm.get_active_learner_ids_today(
            course_id=self.course_overview.id, date_for=self.today)
        assert recs.count() == len(self.course_enrollments)

    def test_get_average_progress_deprecated(self):
        """
        [John] This test needs work. The function it is testing needs work too
        for testability. We don't want to reproduce the function's behavior, we
        just want to be able to set up the source data with expected output and
        go.
        """
        course_enrollments = CourseEnrollment.objects.filter(
            course_id=self.course_overview.id)
        actual = pipeline_cdm.get_average_progress_deprecated(
            course_id=self.course_overview.id,
            date_for=self.today,
            course_enrollments=course_enrollments
            )
        # See tests/mocks/lms/djangoapps/grades/course_grade.py for
        # the source subsection grades that

        # TODO: make the mock data more configurable so we don't have to
        # hardcode the expected value
        assert actual == 0.5

    @mock.patch(
        'figures.metrics.LearnerCourseGrades.course_progress',
        side_effect=PermissionDenied('mock-failure')
    )
    def test_get_average_progress_deprecated_has_error(self, mock_lcg):

        assert PipelineError.objects.count() == 0
        course_enrollments = CourseEnrollment.objects.filter(
            course_id=self.course_overview.id)

        results = pipeline_cdm.get_average_progress_deprecated(
                course_id=self.course_overview.id,
                date_for=self.today,
                course_enrollments=course_enrollments
                )
        assert results == pytest.approx(0.0)
        assert PipelineError.objects.count() == course_enrollments.count()

    def test_get_days_to_complete(self):
        expected = dict(days=self.cert_days_to_complete,
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
        self.date_for = datetime.datetime.utcnow().date()

    def test_extract(self, monkeypatch):
        course_id = self.course_enrollments[0].course_id
        monkeypatch.setattr(figures.pipeline.course_daily_metrics,
                            'bulk_calculate_course_progress_data',
                            lambda **_kwargs: dict(average_progress=0.5))

        results = pipeline_cdm.CourseDailyMetricsExtractor().extract(
            course_id, self.date_for)
        assert results

    def test_when_bulk_calculate_course_progress_data_fails(self,
                                                            monkeypatch,
                                                            caplog):
        course_id = self.course_enrollments[0].course_id

        def mock_bulk(**_kwargs):
            raise Exception('fake exception')

        monkeypatch.setattr(figures.pipeline.course_daily_metrics,
                            'bulk_calculate_course_progress_data',
                            mock_bulk)

        results = pipeline_cdm.CourseDailyMetricsExtractor().extract(
            course_id, self.date_for)

        last_log = caplog.records[-1]
        assert last_log.message.startswith(
            'FIGURES:FAIL bulk_calculate_course_progress_data')
        assert not results['average_progress']


@pytest.mark.django_db
class TestCourseDailyMetricsLoader(object):
    """Provides minimal checking that CourseDailyMetricsLoader works
    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.course_enrollments = [CourseEnrollmentFactory() for i in range(1, 5)]

        if organizations_support_sites():
            self.my_site = SiteFactory(domain='my-site.test')
            self.my_site_org = OrganizationFactory(sites=[self.my_site])
            for ce in self.course_enrollments:
                OrganizationCourseFactory(organization=self.my_site_org,
                                          course_id=str(ce.course.id))
                UserOrganizationMappingFactory(user=ce.user,
                                               organization=self.my_site_org)

        self.student_module = StudentModuleFactory()

    def test_load(self, monkeypatch):
        # pick a course, any course (we'll just pick the first, but doesn't matter which)
        if OPENEDX_RELEASE == GINKGO:
            course_id = self.course_enrollments[0].course_id
        else:
            course_id = self.course_enrollments[0].course.id

        def get_data(self, date_for):
            return {
                'average_progress': 1.0,
                'num_learners_completed': 2,
                'enrollment_count': 3,
                'average_days_to_complete': 0.0,
                'course_id': course_id,
                'date_for': date_for,
                'active_learners_today': 0}

        monkeypatch.setattr(
            figures.pipeline.course_daily_metrics.CourseDailyMetricsLoader,
            'get_data', get_data)
        cdm, created = pipeline_cdm.CourseDailyMetricsLoader(course_id).load()
        assert cdm and created

    def test_load_existing(self):
        course_id = self.course_enrollments[0].course_id
        assert CourseDailyMetrics.objects.count() == 0
        cdm, created = pipeline_cdm.CourseDailyMetricsLoader(course_id).load()
        assert cdm and created
        assert CourseDailyMetrics.objects.count() == 1
        cdm2, created2 = pipeline_cdm.CourseDailyMetricsLoader(course_id).load()
        assert cdm2 and not created2
        assert cdm2.id == cdm.id
        assert CourseDailyMetrics.objects.count() == 1

    @pytest.mark.parametrize('average_progress', [-1.0, -0.01, 1.01])
    def test_load_invalid_data(self, monkeypatch, average_progress):

        course_id = self.course_enrollments[0].course_id
        monkeypatch.setattr(figures.pipeline.course_daily_metrics,
                            'bulk_calculate_course_progress_data',
                            lambda **_kwargs: dict(average_progress=average_progress))

        with pytest.raises(ValidationError) as execinfo:
            assert CourseDailyMetrics.objects.count() == 0
            cdm, created = pipeline_cdm.CourseDailyMetricsLoader(course_id).load()
            assert CourseDailyMetrics.objects.count() == 0
            assert 'average_progress' in execinfo.value.message_dict

    @pytest.mark.skip('Implement me!')
    def test_load_force_update(self):
        pass
