
import datetime

import pytest

from dateutil.parser import parse as dateutil_parse
from dateutil.relativedelta import relativedelta

from figures.helpers import (
    as_course_key,
    as_datetime,
    as_date,
    days_from,
    next_day,
    prev_day,
    previous_months_iterator,
    )


class TestCourseKeyHelper(object):

    @pytest.mark.parametrize('value', [
        ])
    def test_from_valid_string(self, value):
        pass


class TestDateTimeHelper(object):
    '''
    TODO: merge these tests into one and paramtrize the types
    '''
    @pytest.fixture(autouse=True)
    def setup(self):
        self.now = datetime.datetime.now()

    def test_get_now_from_datetime(self):
        expected = self.now
        assert as_datetime(expected) == expected

    def test_get_now_from_str(self):
        format = '%Y-%m-%d %H:%M:%S'
        a_datetime_str = self.now.strftime(format)
        expected = dateutil_parse(a_datetime_str)
        assert as_datetime(a_datetime_str) == expected

    def test_get_now_from_date(self):
        '''
        Returns date at midnight
        '''
        a_date = self.now.date()
        expected = datetime.datetime(
            year=a_date.year,
            month=a_date.month,
            day=a_date.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            )
        assert as_datetime(a_date) == expected


class TestDateHelper(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.now = datetime.datetime.now()

    def test_get_now_from_str(self):
        format = '%Y-%m-%d'
        a_date_str = self.now.strftime(format)
        expected = self.now.date()
        assert as_date(a_date_str) == expected


class TestDeltaDays(object):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.now = datetime.datetime.now()

    @pytest.mark.parametrize('days', range(-2,3))
    def test_days_from(self, days):
        '''TODO: Test with input as a 
        - datetime
        - date
        - str
        - unicode
        '''
        expected = self.now + datetime.timedelta(days=days)
        assert days_from(self.now, days) == expected
        assert days_from(self.now.date(), days) == expected.date()

    def test_next_day(self):
        expected = self.now + datetime.timedelta(days=1)
        assert next_day(self.now) == expected
        assert next_day(self.now.date()) == expected.date()


class TestMonthIterator(object):

    @pytest.mark.parametrize('month_for, months_back, first_month', [
        ((2018,1), 0, datetime.date(2018,1,1)),
        ((2018,1), 6, datetime.date(2017,7,1)),
        ])
    def test_previous_months_iterator(self, month_for, months_back, first_month):

        def as_month_tuple(month):
            return (month.year, month.month)
        #expected
        expected_vals = []
        for i in range(months_back):
            a_month = first_month+relativedelta(months=i)
            expected_vals.append(
                (a_month.year, a_month.month)
                )
        #add month_for
        expected_vals.append(month_for)

        vals = list(previous_months_iterator(month_for, months_back))
        #import pdb; pdb.set_trace()
        assert vals == expected_vals
