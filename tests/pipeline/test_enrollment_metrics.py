
from __future__ import absolute_import
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import mock
import pytest

from django.utils.timezone import utc
from figures.compat import CourseEnrollment, StudentModule

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
    OrganizationFactory,
    OrganizationCourseFactory,
    SiteFactory,
    StudentModuleFactory,
)
from tests.helpers import organizations_support_sites
from six.moves import range


if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory


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
    StudentModuleFactory()

    def mock_metrics(course_enrollment, **_kwargs):
        return mapping[course_enrollment.course_id]

    monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                        lambda val: SiteFactory())
    monkeypatch.setattr('figures.pipeline.enrollment_metrics.collect_metrics_for_enrollment',
                        mock_metrics)

    monkeypatch.setattr('figures.pipeline.enrollment_metrics.course_enrollments_for_course',
                        lambda val: CourseEnrollment.objects.all())
    # monkeypatch.setattr('figures.pipeline.enrollment_metrics.student_modules_for_course_enrollment',
    #                     mock_get_student_modules)
    monkeypatch.setattr('figures.pipeline.enrollment_metrics.student_modules_for_course_enrollment',
                        lambda **_kwargs: StudentModule.objects.all())
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
        self.today = date.today()
        self.site = SiteFactory()
        if organizations_support_sites():
            self.org = OrganizationFactory(sites=[self.site])
        else:
            self.org = OrganizationFactory()

        self.datetime_1 = datetime(2020, 2, 2, tzinfo=utc)
        self.datetime_2 = self.datetime_1 + relativedelta(months=1)  # future of date_1
        self.course_overview = CourseOverviewFactory()
        self.course_enrollment = CourseEnrollmentFactory(course_id=self.course_overview.id)
        self.course_enrollment_2 = CourseEnrollmentFactory(course_id=self.course_overview.id)
        if organizations_support_sites():
            OrganizationCourseFactory(organization=self.org,
                                      course_id=str(self.course_overview.id))
            UserOrganizationMappingFactory(organization=self.org,
                                           user=self.course_enrollment.user)
            UserOrganizationMappingFactory(organization=self.org,
                                           user=self.course_enrollment_2.user)
        self.student_modules = [
            StudentModuleFactory(student=self.course_enrollment.user,
                                 course_id=self.course_enrollment.course_id,
                                 modified=self.datetime_1),
            StudentModuleFactory(student=self.course_enrollment.user,
                                 course_id=self.course_enrollment.course_id,
                                 modified=self.datetime_2),
            # This student module does not belong to the user in course_enrollment
            StudentModuleFactory(course_id=self.course_enrollment.course_id,
                                 modified=self.datetime_2)
        ]
        self.learner_sm = StudentModule.objects.filter(
            course_id=self.course_enrollment.course_id,
            student=self.course_enrollment.user).order_by('-modified')
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

    def create_lcgm(self, date_for, course_enrollment):
        """Helper to create an LCGM record with the given `date_for`
        """
        return LearnerCourseGradeMetricsFactory(
            course_id=str(course_enrollment.course_id),
            user=course_enrollment.user,
            date_for=date_for,
            points_possible=self.progress_data['points_possible'],
            points_earned=self.progress_data['points_earned'],
            sections_worked=self.progress_data['sections_worked'],
            sections_possible=self.progress_data['count']
        )

    def test_has_no_lcgm_and_needs_update(self, monkeypatch):
        """We have an SM record, but no LCGM record

        The function under test should return a new LCGM record
        """
        assert not LearnerCourseGradeMetrics.objects.count()
        monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                            lambda val: self.site)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics._collect_progress_data',
                            lambda val: self.progress_data)

        metrics = collect_metrics_for_enrollment(site=self.site,
                                                 course_enrollment=self.course_enrollment,
                                                 date_for=self.today,
                                                 student_modules=self.learner_sm)

        self.check_response_metrics(metrics, self.progress_data)
        assert LearnerCourseGradeMetrics.objects.count() == 1

    def test_has_lcgm_and_needs_update(self, monkeypatch):
        """We have an LCGM record, but it is not up to date with the SM

        The function under test should return a new LCGM

        TODO: Add test where we pass in `date_for` to the function under test
        """
        assert not LearnerCourseGradeMetrics.objects.filter(
            user=self.course_enrollment.user,
            course_id=str(self.course_enrollment.course_id)).exists()
        lcgm = self.create_lcgm(date_for=self.datetime_1.date(),
                                course_enrollment=self.course_enrollment)
        # lcgm = LearnerCourseGradeMetricsFactory()
        # Maybe remove these, but first make code sample to show how to mock
        # multisite. This helps in abstracting our tests, but risks wrong
        # behavior in production
        # If we do monkeypatch like this, we will need to also monkeypatch the
        # user belonging to the site
        monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                            lambda val: self.site)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics._collect_progress_data',
                            lambda val: self.progress_data)

        # assert isinstance(lcgm.date_for, date)
        # import pdb; pdb.set_trace()
        assert _enrollment_metrics_needs_update(lcgm, self.learner_sm[0])
        metrics = collect_metrics_for_enrollment(site=self.site,
                                                 course_enrollment=self.course_enrollment,
                                                 date_for=self.today,
                                                 student_modules=self.learner_sm)

        self.check_response_metrics(metrics, self.progress_data)
        assert metrics != lcgm

        # This works because we pick dates in the past. Better is to  fix this
        # by either using freezegun or monkeypatching `_new_enrollment_metrics_record
        assert metrics.date_for >= self.datetime_2.date()

    def test_does_not_need_update(self, monkeypatch):
        """We have an LCGM record that is up to date with the SM

        The function under test should return the LCGM

        TODO: Add test where we pass in `date_for` to the function under test
        """
        lcgm = self.create_lcgm(date_for=self.datetime_2.date(),
                                course_enrollment=self.course_enrollment)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                            lambda val: self.site)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics._collect_progress_data',
                            lambda val: self.progress_data)

        metrics = collect_metrics_for_enrollment(site=self.site,
                                                 course_enrollment=self.course_enrollment,
                                                 date_for=self.today,
                                                 student_modules=self.learner_sm)

        self.check_response_metrics(metrics, self.progress_data)
        assert metrics == lcgm
        assert metrics.date_for == self.datetime_2.date()

    def test_no_update_no_lcgm_no_sm(self, monkeypatch):
        """We have neither an LCGM nor an SM record

        The function under test should return None
        """
        monkeypatch.setattr('figures.pipeline.enrollment_metrics.get_site_for_course',
                            lambda val: self.site)
        monkeypatch.setattr('figures.pipeline.enrollment_metrics._collect_progress_data',
                            lambda val: self.progress_data)
        # Create a course enrollment for which we won't have student module records
        learner_sm = StudentModule.objects.filter(course_id=self.course_enrollment_2.course_id,
                                                  student=self.course_enrollment_2.user)
        metrics = collect_metrics_for_enrollment(site=self.site,
                                                 course_enrollment=self.course_enrollment_2,
                                                 date_for=self.today,
                                                 student_modules=learner_sm)
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
        ce = CourseEnrollmentFactory(course_id=self.course_enrollment.course_id)
        if organizations_support_sites():
            UserOrganizationMappingFactory(organization=self.org, user=ce.user)
        lcgm = LearnerCourseGradeMetricsFactory(course_id=ce.course_id, user=ce.user)
        
        ce_sm = StudentModule.objects.filter(course_id=ce.course_id, student_id=ce.user.id)
        assert not ce_sm
        metrics = collect_metrics_for_enrollment(site=self.site,
                                                 course_enrollment=ce,
                                                 date_for=self.today,
                                                 student_modules=ce_sm)
        assert not metrics
        # assert not StudentModule.objects.filter(course_id=ce.course_id)

    def test_arg_sm_acts_as_no_arg_sm(self):
        """
        Test that we get the same results if we don't pass a student_module arg
        as when we do for the same set of student module records for the
        course enrollment
        """
        pass


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

    def test_existence_yes_lcgm_no_sm_is_false(self, caplog):
        lcgm = LearnerCourseGradeMetricsFactory()
        assert not _enrollment_metrics_needs_update(lcgm, None)
        last_log = caplog.records[-1]
        assert last_log.message.startswith('FIGURES:PIPELINE:LCGM')
        # import pdb; pdb.set_trace()
        assert lcgm.course_id in last_log.message
        assert str(lcgm.id) in last_log.message
        assert str(lcgm.user.id) in last_log.message


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
