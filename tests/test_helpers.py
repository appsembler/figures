from __future__ import absolute_import
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
    first_last_days_for_month,
    import_from_path,
    )

from tests.factories import COURSE_ID_STR_TEMPLATE
import six
from six.moves import range


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
        a_datetime_str = six.text_type(self.now.strftime(format))
        expected = dateutil_parse(a_datetime_str).replace(tzinfo=utc)
        assert isinstance(a_datetime_str, six.text_type)
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
        a_date_str = six.text_type(self.now.strftime(format))
        expected = self.now.date()
        assert isinstance(a_date_str, six.text_type)
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

    @pytest.mark.parametrize('days', list(range(-2, 3)))
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

    @pytest.mark.parametrize('month_for, months_back', [
        ((2018, 1, 31), 0),
        ((2018, 1, 31), 6),
        ((2020, 4, 30), 2),  # let's use a leap year
    ])
    def test_previous_months_iterator(self, month_for, months_back):
        expected_vals = []
        month_for = datetime.date(year=month_for[0], month=month_for[1], day=month_for[2])
        for i in range(max(1, months_back), 0, -1):  # e.g., 6, 5, 4, 3, 2, 1
            a_month = month_for - relativedelta(months=i - 1)
            last_day_in_month = calendar.monthrange(a_month.year, a_month.month)[1]
            expected_vals.append(
                (a_month.year, a_month.month, last_day_in_month)
            )
        vals = list(previous_months_iterator(month_for, months_back))
        assert vals == expected_vals

def test_first_last_days_for_month():
    month_for = '2/2020'
    month = 2
    year = 2020
    first_day, last_day = first_last_days_for_month(month_for=month_for)
    assert first_day.month == month
    assert last_day.month == month
    assert first_day.year == year
    assert last_day.year == year
    assert first_day.day == 1
    assert last_day.day == 29


def test_import_from_path_working():
    utc_tz_path = 'django.utils.timezone:utc'
    imported_utc = import_from_path(utc_tz_path)
    assert imported_utc is utc, 'Should import the utc variable correctly'


def test_import_from_path_failing():
    utc_tz_path = 'django.utils.timezone:non_existent_variable'
    with pytest.raises(AttributeError):
        # Should raise an AttributeError because the helper is using getattr()
        import_from_path(utc_tz_path)


def test_import_from_path_missing_module():
    utc_tz_path = 'non_existent_module.submodule:some_variable'
    with pytest.raises(ImportError):
        # Should raise an ImportError because the module does not exist
        import_from_path(utc_tz_path)


def test_import_from_bad_syntax():
    utc_tz_path = 'not a path'
    with pytest.raises(ValueError):
        # Malformed path
        import_from_path(utc_tz_path)
