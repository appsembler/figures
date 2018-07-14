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
import pytest


#from django.db import models

from figures import metrics

from tests.factories import SiteDailyMetricsFactory


# TODO:

# - build set of User, StudentModule, CourseOverview objects to test the
# StudentModule based methods and classes


@pytest.mark.django_db
class TestGetMonthlySiteMetrics(object):
    '''
    This test also exercises the time period getters used in
    metrics.get_monthly_site_metrics
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.today = datetime.datetime.now()
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


@pytest.mark.django_db
class TestTimePeriodGetters(object):
    '''The purpose of this class is to test the individual time period getter
    functions

    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        pass

    @pytest.mark.skip(reason='Test not implemented yet')
    def test_get_active_users_for_time_period(self):
        pass

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

