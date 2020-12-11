
from __future__ import absolute_import
from datetime import datetime
from dateutil.relativedelta import relativedelta
import mock
import pytest

from django.utils.timezone import utc
from figures.compat import StudentModule

from figures.helpers import is_multisite
from figures.models import LearnerCourseGradeMetrics
from figures.pipeline.enrollment_metrics import (
    calculate_average_progress,
    bulk_calculate_course_progress_data,
    collect_metrics_for_enrollment,
    _enrollment_metrics_needs_update,
    _new_enrollment_metrics_record,
    _collect_progress_data,
)
from figures.sites import UnlinkedCourseError

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    LearnerCourseGradeMetricsFactory,
    SiteFactory,
    StudentModuleFactory,
)
from six.moves import range


@pytest.mark.django_db
def test_bulk_calculate_course_progress_data_happy_path(db, monkeypatch):
    """Tests 'bulk_calculate_course_progress_data' function

    The function under test iterates over a set of course enrollment records,
    So we create a couple of records to iterate over and mock the collect
    function
    """
    course_overview = CourseOverviewFactory()
    course_enrollments = [CourseEnrollmentFactory(
        course_id=course_overview.id) for i in range(2)]
    mapping = {ce.course_id: LearnerCourseGradeMetricsFactory(
        course_id=str(ce.course_id),
        user=ce.user,
        sections_worked=1,
        sections_possible=2) for ce in course_enrollments
    }

    def mock_metrics(course_enrollment, **_kwargs):
        return mapping[course_enrollment.course_id]

    monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                        lambda val: SiteFactory())
    monkeypatch.setattr('figures.pipeline.enrollment_metrics.collect_metrics_for_enrollment',
                        mock_metrics)
    data = bulk_calculate_course_progress_data(course_overview.id)
    assert data['average_progress'] == 0.5


@pytest.mark.skipif(not is_multisite(),
                    reason='Standalone always returns a site')
@pytest.mark.django_db
def test_bulk_calculate_course_progress_unlinked_course_error(db, monkeypatch):
    """Tests 'bulk_calculate_course_progress_data' function

    The function under test iterates over a set of course enrollment records,
    So we create a couple of records to iterate over and mock the collect
    function
    """
    course_overview = CourseOverviewFactory()
    course_enrollments = [CourseEnrollmentFactory(
        course_id=course_overview.id) for i in range(2)]
    mapping = {ce.course_id: LearnerCourseGradeMetricsFactory(
        course_id=str(ce.course_id),
        user=ce.user,
        sections_worked=1,
        sections_possible=2) for ce in course_enrollments
    }

    def mock_metrics(course_enrollment, **_kwargs):
        return mapping[course_enrollment.course_id]

    monkeypatch.setattr('figures.pipeline.enrollment_metrics.collect_metrics_for_enrollment',
                        mock_metrics)
    with pytest.raises(UnlinkedCourseError) as e_info:
        data = bulk_calculate_course_progress_data(course_overview.id)

    # assert data['average_progress'] == 0.5


@pytest.mark.django_db
def test_bulk_calculate_course_progress_no_enrollments(db, monkeypatch):
    """This tests when there is a new course with no enrollments
    """
    monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                        lambda val: SiteFactory())
    course_overview = CourseOverviewFactory()
    data = bulk_calculate_course_progress_data(course_overview.id)
    assert data['average_progress'] == 0.0


@pytest.mark.parametrize('progress_percentages, expected_result', [
    (None, 0.0),
    ([], 0.0),
    ([0, 0.25, 0.5, 0.75, 1.0], 0.5),
])
def test_calculate_average_progress_happy_path(progress_percentages, expected_result):
    """Tests 'calculate_average_progress_happy_path' function

    The function under test is a simple average calculation with formatting
    """
    average_progress = calculate_average_progress(progress_percentages)
    assert average_progress == expected_result


@pytest.mark.django_db
class TestCollectMetricsForEnrollment(object):
    """Tests 'collect_metrics_for_enrollment' function

    The function under test does the following:

    Given a course enrollment,
      1. Get the most recent StudentModule (SM) record, if it exists
      2. Get the most recent LearnerCourseGradeMetrics (LCGM) record, if it exists
      3. Decide if we need to add a new LCGM record for the enrollment or use
         the most recent one, if it exists
      4. Collect new data from the platform if we need to update the enrollment's
         metrics
      5. Add a new LCGM record if we are collecting new metrics data
      6. Return the new LCGM record if created, else return the existing record
         found
    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = SiteFactory()
        self.date_1 = datetime(2020, 2, 2, tzinfo=utc)
        self.date_2 = self.date_1 + relativedelta(months=1)  # future of date_1
        self.course_enrollment = CourseEnrollmentFactory()
        self.student_modules = [
            StudentModuleFactory(student=self.course_enrollment.user,
                                 course_id=self.course_enrollment.course_id,
                                 modified=self.date_1),
            StudentModuleFactory(student=self.course_enrollment.user,
                                 course_id=self.course_enrollment.course_id,
                                 modified=self.date_2)]
        self.progress_data = dict(points_possible=100,
                                  points_earned=25,
                                  sections_worked=4,
                                  count=5)

    def check_response_metrics(self, obj, data):
        """Helper method checks LCGM object's data
        """
        assert obj.points_possible == data['points_possible']
        assert obj.points_earned == data['points_earned']
        assert obj.sections_worked == data['sections_worked']
        assert obj.sections_possible == data['count']

    def create_lcgm(self, date_for):
        """Helper to create an LCGM record with the given `date_for`
        """
        return LearnerCourseGradeMetricsFactory(
            course_id=str(self.course_enrollment.course_id),
            user=self.course_enrollment.user,
            date_for=date_for,
            points_possible=self.progress_data['points_possible'],
            points_earned=self.progress_data['points_earned'],
            sections_worked=self.progress_data['sections_worked'],
            sections_possible=self.progress_data['count']
        )

    def test_needs_update_no_lcgm(self, monkeypatch):
        """We have an SM record, but no LCGM record

        The function under test should return a new LCGM record
        """
        assert not LearnerCourseGradeMetrics.objects.count()
        monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                            lambda val: self.site)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics._collect_progress_data',
                            lambda val: self.progress_data)

        course_sm = StudentModule.objects.filter(course_id=self.course_enrollment.course_id)
        metrics = collect_metrics_for_enrollment(site=self.site,
                                                 course_enrollment=self.course_enrollment,
                                                 course_sm=course_sm)

        self.check_response_metrics(metrics, self.progress_data)
        assert LearnerCourseGradeMetrics.objects.count() == 1

    def test_needs_update_has_lcgm(self, monkeypatch):
        """We have an LCGM record, but it is not up to date with the SM

        The function under test should return a new LCGM

        TODO: Add test where we pass in `date_for` to the function under test
        """
        lcgm = self.create_lcgm(date_for=self.date_1)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                            lambda val: self.site)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics._collect_progress_data',
                            lambda val: self.progress_data)
        course_sm = StudentModule.objects.filter(course_id=self.course_enrollment.course_id)
        metrics = collect_metrics_for_enrollment(site=self.site,
                                                 course_enrollment=self.course_enrollment,
                                                 course_sm=course_sm)

        self.check_response_metrics(metrics, self.progress_data)
        assert metrics != lcgm

        # This works because we pick dates in the past. Better is to  fix this
        # by either using freezegun or monkeypatching `_new_enrollment_metrics_record
        assert metrics.date_for >= self.date_2.date()

    def test_does_not_need_update(self, monkeypatch):
        """We have an LCGM record that is up to date with the SM

        The function under test should return the LCGM

        TODO: Add test where we pass in `date_for` to the function under test
        """
        lcgm = self.create_lcgm(date_for=self.date_2.date())
        monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                            lambda val: self.site)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics._collect_progress_data',
                            lambda val: self.progress_data)
        course_sm = StudentModule.objects.filter(course_id=self.course_enrollment.course_id)
        metrics = collect_metrics_for_enrollment(site=self.site,
                                                 course_enrollment=self.course_enrollment,
                                                 course_sm=course_sm)

        self.check_response_metrics(metrics, self.progress_data)
        assert metrics == lcgm
        assert metrics.date_for == self.date_2.date()

    def test_no_update_no_lcgm_no_sm(self, monkeypatch):
        """We have neither an LCGM nor an SM record

        The function under test should return None
        """
        monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                            lambda val: self.site)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics._collect_progress_data',
                            lambda val: self.progress_data)
        # Create a course enrollment for which we won't have student module records
        ce = CourseEnrollmentFactory()
        course_sm = StudentModule.objects.filter(course_id=ce.course_id)
        metrics = collect_metrics_for_enrollment(site=self.site,
                                                 course_enrollment=ce,
                                                 course_sm=course_sm)
        assert not metrics

    def test_no_update_has_lcgm_no_sm(self, monkeypatch):
        """We have an LCGM but not an SM record

        The function under test should return the existing LCGM
        """
        monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                            lambda val: self.site)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics._collect_progress_data',
                            lambda val: self.progress_data)
        # Create a course enrollment for which we won't have student module records
        ce = CourseEnrollmentFactory()
        lcgm = LearnerCourseGradeMetricsFactory(course_id=ce.course_id, user=ce.user)
        course_sm = StudentModule.objects.filter(course_id=ce.course_id)
        metrics = collect_metrics_for_enrollment(site=self.site,
                                                 course_enrollment=ce,
                                                 course_sm=course_sm)
        assert metrics == lcgm
        assert not StudentModule.objects.filter(course_id=ce.course_id)


@pytest.mark.django_db
class TestEnrollmentMetricsUpdateCheck(object):
    """Tests the `_enrollment_metrics_needs_update` function performs as expected

    Quick test of the different states and expected results. Should be reworked

    We should be able to collapse these tests into one using parametrize. However,
    we don't want conditionals and some tests call for testing dates and others
    existance. So for now, a little less DRY with individual tests for each
    conditional in the function
    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.student_module = StudentModuleFactory()

    def test_existence_no_lcgm_no_sm_is_false(self):
        """Test if there is not a LearnerCourseGradeMetrics  record and not a
        SiteModule, then it returns false
        """
        assert not _enrollment_metrics_needs_update(None, None)

    def test_existence_no_lcgm_yes_sm_is_true(self):
        assert _enrollment_metrics_needs_update(None, self.student_module)

    def test_existence_yes_lcgm_no_sm_is_false(self):
        path = 'figures.pipeline.enrollment_metrics.log_error'
        with mock.patch(path) as mock_log_error:
            assert not _enrollment_metrics_needs_update(LearnerCourseGradeMetricsFactory(), None)
            mock_log_error.assert_called()

    def test_dates_lcgm_is_current_is_false(self):
        lcgm = LearnerCourseGradeMetricsFactory(
            date_for=self.student_module.modified.date())
        assert not _enrollment_metrics_needs_update(lcgm, self.student_module)

    def test_dates_lcgm_is_future_is_false(self):
        """
        Note: This should probably be an error state
        """
        lcgm = LearnerCourseGradeMetricsFactory(
            date_for=self.student_module.modified.date() + relativedelta(days=1))
        assert not _enrollment_metrics_needs_update(lcgm, self.student_module)

    def test_dates_lcgm_is_past_is_true(self):
        lcgm = LearnerCourseGradeMetricsFactory(
            date_for=self.student_module.modified.date() - relativedelta(days=1))
        assert _enrollment_metrics_needs_update(lcgm, self.student_module)


@pytest.mark.django_db
class TestAddEnrollmentMetricsRecord(object):
    """Tests the `_new_enrollment_metrics_record` function

    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = SiteFactory()
        self.course_enrollment = CourseEnrollmentFactory()
        self.date_for = datetime.utcnow().replace(tzinfo=utc).date()

    def test_happy_path(self):
        """Basic creation check
        """
        progress_data = dict(
            points_possible=10,
            points_earned=5,
            count=22,  # sections possible
            sections_worked=11
        )
        obj = _new_enrollment_metrics_record(site=self.site,
                                             course_enrollment=self.course_enrollment,
                                             progress_data=progress_data,
                                             date_for=self.date_for)
        assert obj


@pytest.mark.django_db
def test_collect_progress_data(db, monkeypatch):
    """Tests the `_collect_progress_data` function

    The function under test instantiates a LearnerCourseGrade object, calls its
    `progress`

    We can use the default values created from the mock `LearnerCourseGrades`
    class
    """
    student_module = StudentModuleFactory()
    progress_data = _collect_progress_data(student_module)

    # Simply checking the keys
    assert set(progress_data.keys()) == set(['count',
                                             'sections_worked',
                                             'points_possible',
                                             'points_earned'])
