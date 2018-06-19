'''
Helper functions to make data handling and conversions easier


'''

import datetime
from dateutil.parser import parse as dateutil_parse
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locator import CourseLocator


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
        # Return the end of the day
        return datetime.datetime(
            year=val.year,
            month=val.month,
            day=val.day,
            # hour=0,
            # minute=59,
            # second=59
            )

    elif isinstance(val, basestring):
        return dateutil_parse(val)
    else:
        raise TypeError(
            'value of type "{}" cannot be converted to a datetime object'.format(
                type(val)))

def as_date(val):
    if isinstance(val, datetime.date):
        return val
    else:
        return as_datetime(val).date()

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
