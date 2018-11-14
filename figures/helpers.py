'''
Helper functions to make data handling and conversions easier
'''

import calendar
import datetime
from django.utils.timezone import utc

from dateutil.parser import parse as dateutil_parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY

from opaque_keys.edx.keys import CourseKey


def as_course_key(course_id):
    '''Returns course id as a CourseKey instance

    Convenience method to return the paramater unchanged if it is of type
    ``CourseKey`` or attempts to convert to ``CourseKey`` if of type str or
    unicode.

    Raises TypeError if an unsupported type is provided
    '''
    if isinstance(course_id, CourseKey):
        return course_id
    elif isinstance(course_id, basestring):
        return CourseKey.from_string(course_id)
    else:
        raise TypeError('Unable to convert course id with type "{}"'.format(
            type(course_id)))


def as_datetime(val):
    '''
    TODO: Add arg flag to say if caller wants end of day, beginning of day
    or a particular time of day if the param is a datetime.date obj
    '''
    if isinstance(val, datetime.datetime):
        return val
    elif isinstance(val, datetime.date):
        # Return the end of the day, set timezone to be UTC
        return datetime.datetime(
            year=val.year,
            month=val.month,
            day=val.day,
            ).replace(tzinfo=utc)

    elif isinstance(val, basestring):
        return dateutil_parse(val).replace(tzinfo=utc)
    else:
        raise TypeError(
            'value of type "{}" cannot be converted to a datetime object'.format(
                type(val)))


def as_date(val):
    '''Casts the value to a ``datetime.date`` object if possible

    Else raises ``TypeError``
    '''
    # Important to check if datetime first because datetime.date objects
    # pass the isinstance(obj, datetime.date) test
    if isinstance(val, datetime.datetime):
        return val.date()
    elif isinstance(val, datetime.date):
        return val
    elif isinstance(val, basestring):
        return dateutil_parse(val).date()
    else:
        raise TypeError(
            'date cannot be of type "{}".'.format(type(val)) +
            ' It must be able to be cast to a datetime.date')


def days_from(val, days):
    if isinstance(val, datetime.datetime):
        return as_datetime(val) + datetime.timedelta(days=days)
    elif isinstance(val, datetime.date):
        return as_date(val) + datetime.timedelta(days=days)
    else:
        raise TypeError(
            'val of type "{}" is not supported.'.format(type(val)))


def next_day(val):
    return days_from(val, 1)


def prev_day(val):
    return days_from(val, -1)


# TODO: Consider changing name to 'months_back_iterator' or similar
# TODO: implement or removed include_month_for
def previous_months_iterator(month_for, months_back, include_month_for=False):
    '''Iterator returns a year,month tulbe for n months including the month_for

    month_for is either a date, datetime, or tuple with year and month
    months back is the number of months to iterate

    includes the month_for
    '''

    if isinstance(month_for, tuple):
        # TODO make sure we've got just two values in the tuple
        month_for = datetime.date(year=month_for[0], month=month_for[1], day=1)
    if isinstance(month_for, (datetime.datetime, datetime.date)):
        start_month = month_for - relativedelta(months=months_back)

    for dt in rrule(freq=MONTHLY, dtstart=start_month, until=month_for):
        last_day_of_month = calendar.monthrange(dt.year, dt.month)[1]
        yield (dt.year, dt.month, last_day_of_month)
