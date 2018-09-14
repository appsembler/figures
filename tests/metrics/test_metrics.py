'''

For these tests, we need to build at least one set of data that includes

* Data for a set of days that include data points both before, during, and after
  each time period for which we test
* Models populated:
** CourseOverview
** CourseEnrollment
** StudentModule
** CourseDailyMetrics
** SiteDailyMetrics
** User
** UserProfile

Initially:
* we need to test for when the date_for is the current date
* We are going to do minimal testing just to make sure the functions can be
  called succesfully. Correctness checking to follow


'''
import datetime

from dateutil.rrule import rrule, DAILY

from django.utils import timezone
import pytest


from figures import metrics

from courseware.models import StudentModule
from tests.factories import (
    CourseOverviewFactory,
    SiteDailyMetricsFactory,
    StudentModuleFactory,
    UserFactory,
    )


# TODO:

# - build set of User, StudentModule, CourseOverview objects to test the
# StudentModule based methods and classes

DEFAULT_START_DATE = datetime.datetime(2018,01,01, 0, 0, tzinfo=timezone.get_current_timezone())
DEFAULT_END_DATE = datetime.datetime(2018,06,01, 0, 0, tzinfo=timezone.get_current_timezone())


@pytest.mark.django_db
class TestGetMonthlySiteMetrics(object):
    '''
    This test also exercises the time period getters used in
    metrics.get_monthly_site_metrics
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.today = datetime.datetime.utcnow()
        self.site_daily_metrics = None
        self.expected_keys = (
            'monthly_active_users',
            'total_site_users',
            'total_site_courses',
            'total_course_enrollments',
            'total_course_completions',)

    @pytest.mark.skip(reason='Test not implemented yet')
    # @pytest.mark.paramtrize('date_for', [
    #     (None),
    #     (self.today),
    #     ])
    def test_get_today(self):
        date_for = self.today
        data = metrics.get_monthly_site_metrics(date_for=date_for)
        assert set(data.keys()) == self.expected_keys


@pytest.mark.django_db
class TestGetMonthlyActiveUsers(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site_daily_metrics = None


    @pytest.mark.skip(reason='Test not implemented yet')
    def test_get(self):
        pass



def create_student_module_test_data(start_date, end_date):
    '''

    NOTE: There are many combinations of unique students, courses, and student
    state. We're going to start with a relatively simple set

    1. A single course
    2. A single set per student (learner)
    3. a small number of students to reduce test run time

    If we create a record per day then we can work off of a unique datapoint
    per day
    '''
    student_modules = []
    user = UserFactory()
    course_overview = CourseOverviewFactory()

    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        student_modules.append(StudentModuleFactory(
            student=user,
            course_id=course_overview.id,
            created=dt,
            modified=dt,
            ))

    # we'll return everything we create
    return dict(
        user=user,
        course_overview=course_overview,
        student_modules=student_modules,
    )

@pytest.mark.django_db
class TestTimePeriodGetters(object):
    '''The purpose of this class is to test the individual time period getter
    functions

    TODO: Pull out the start/end date setup into a 'TimeSeriesTest' base class
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        #self.tzinfo = timezone.get_current_timezone()

        self.data_start_date = DEFAULT_START_DATE
        self.data_end_date = DEFAULT_END_DATE
        self.student_module_data = create_student_module_test_data(
            start_date=self.data_start_date,
            end_date=self.data_end_date)

    @pytest.mark.skip(reason='Test fails. Need to investigate')
    def test_get_active_users_for_time_period(self):
        '''

        '''

        count = metrics.get_active_users_for_time_period(
            start_date=self.data_start_date,
            end_date=self.data_end_date,
            )

        assert count == StudentModule.objects.all().count()


    @pytest.mark.skip(reason='Test not implemented yet')
    def test_get_total_course_completions_for_time_period(self):
        pass

    @pytest.mark.skip(reason='Test not implemented yet')
    def test_get_total_enrolled_users_for_time_period(self):
        pass

    @pytest.mark.skip(reason='Test not implemented yet')
    def test_get_total_site_courses_for_time_period(self):
        pass

    @pytest.mark.skip(reason='Test not implemented yet')
    def test_get_total_site_users_for_time_period(self):
        pass

    @pytest.mark.skip(reason='Test not implemented yet')
    def test_get_total_site_users_joined_for_time_period(self):
        pass

