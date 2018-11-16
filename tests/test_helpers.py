 
import calendar
import datetime
from django.utils.timezone import utc

import pytest

from dateutil.parser import parse as dateutil_parse
from dateutil.relativedelta import relativedelta

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locator import CourseLocator

from figures.helpers import (
    as_course_key,
    as_datetime,
    as_date,
    days_from,
    next_day,
    prev_day,
    previous_months_iterator,
    )

from tests.factories import COURSE_ID_STR_TEMPLATE

class TestCourseKeyHelper(object):
    '''Tests the figures.helpers.as_course_key method
    '''
    def setup(self):
        self.course_key_string = COURSE_ID_STR_TEMPLATE.format(1)
        self.course_key = CourseKey.from_string(
            self.course_key_string)

    def test_from_valid_string(self):
        course_key = as_course_key(self.course_key_string)
        assert isinstance(course_key, CourseKey)
        assert course_key == self.course_key
        assert course_key is not self.course_key

    def test_from_invalid_string(self):
        with pytest.raises(InvalidKeyError):
            as_course_key('some invalid string')

    def test_from_course_key(self):
        course_key = as_course_key(self.course_key)
        assert isinstance(course_key, CourseKey)
        assert course_key == self.course_key
        assert course_key is self.course_key

    def test_from_course_locator(self):
        course_locator = CourseLocator.from_string(
            self.course_key_string)
        course_key = as_course_key(course_locator)
        assert isinstance(course_key, CourseKey)
        assert course_key == self.course_key
        assert course_key is course_locator

    def test_from_invalid_type(self):
        with pytest.raises(TypeError):
            as_course_key(dict(foo='bar'))


class TestDateTimeHelper(object):
    '''
    TODO: merge these tests into one and paramtrize the types
    '''
    @pytest.fixture(autouse=True)
    def setup(self):
        self.now = datetime.datetime(2018, 6, 1)

    def test_get_now_from_datetime(self):
        expected = self.now
        assert as_datetime(expected) == expected

    def test_get_now_from_str(self):
        format = '%Y-%m-%d %H:%M:%S'
        a_datetime_str = self.now.strftime(format)
        expected = dateutil_parse(a_datetime_str).replace(tzinfo=utc)
        assert isinstance(a_datetime_str, str)
        assert as_datetime(a_datetime_str) == expected

    def test_get_now_from_unicode(self):
        format = '%Y-%m-%d %H:%M:%S'
        a_datetime_str = unicode(self.now.strftime(format))
        expected = dateutil_parse(a_datetime_str).replace(tzinfo=utc)
        assert isinstance(a_datetime_str, unicode)
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
            ).replace(tzinfo=utc)
        assert as_datetime(a_date) == expected

    def test_get_now_from_invalid_type(self):
        with pytest.raises(TypeError):
            as_datetime(dict(foo='bar'))

    def test_get_now_from_invalid_string(self):
        with pytest.raises(ValueError):
            as_datetime('Hello World')


class TestDateHelper(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.now = datetime.datetime(2018, 6, 1)

    def test_get_now_from_str(self):
        format = '%Y-%m-%d'
        a_date_str = self.now.strftime(format)
        expected = self.now.date()
        assert isinstance(a_date_str, str)
        assert as_date(a_date_str) == expected

    def test_get_now_from_unicode(self):
        format = '%Y-%m-%d'
        a_date_str = unicode(self.now.strftime(format))
        expected = self.now.date()
        assert isinstance(a_date_str, unicode)
        assert as_date(a_date_str) == expected

    def test_get_now_from_date(self):
        expected = self.now.date()
        assert isinstance(expected, datetime.date)
        assert as_date(expected) == expected

    def test_get_now_from_datetime(self):
        expected = self.now.date()
        assert isinstance(self.now, datetime.datetime)
        assert as_date(self.now) == expected

    def test_get_now_from_invalid_type(self):
        with pytest.raises(TypeError):
            as_date(dict(foo='bar'))

    def test_get_now_from_invalid_string(self):
        with pytest.raises(ValueError):
            as_date('Hello World')


class TestDeltaDays(object):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.now = datetime.datetime(2018, 6, 1)

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

    def test_invalid_val(self):
        with pytest.raises(TypeError):
            days_from("some string", 1)


    def test_prev_day(self):
        expected = self.now + datetime.timedelta(days=-1)
        assert prev_day(self.now) == expected


class TestMonthIterator(object):

    @pytest.mark.parametrize('month_for, months_back, first_month', [
        ((2018,1,31), 0, datetime.date(2018,1,1)),
        ((2018,1,31), 6, datetime.date(2017,7,1)),
        ])
    def test_previous_months_iterator(self, month_for, months_back, first_month):

        def as_month_tuple(month):
            return (month.year, month.month)
        expected_vals = []
        for i in range(months_back):
            a_month = first_month+relativedelta(months=i)
            last_day_in_month = calendar.monthrange(a_month.year, a_month.month)[1]
            expected_vals.append(
                (a_month.year, a_month.month, last_day_in_month)
                )
        expected_vals.append(month_for)

        vals = list(previous_months_iterator(month_for, months_back))
        assert vals == expected_vals
