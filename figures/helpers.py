'''
Helper functions to make data handling and conversions easier

Todo: add 'timelord' datetime/date helpers module
'''

import calendar
import datetime

from dateutil.parser import parse as dateutil_parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY

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

def yesterday():
    '''
    return yesteday as a datetime.date object
    '''
    return days_from(datetime.datetime.now().date())


def previous_months_iterator(month_for, months_back, include_month_for=False):
    '''Iterator returns a year,month tulbe for n months including the month_for

    month_for is either a date, datetime, or tuple with year and month
    months back is the number of months to iterate

    
    includes the month_for
    '''

    if isinstance(month_for, tuple):
        # TODO make sure we've got just two values in the tuple
        month_for = datetime.date(year=month_for[0], month=month_for[1], day=1)
    if isinstance(month_for,(datetime.datetime, datetime.date)):
        start_month = month_for - relativedelta(months=months_back)

    for dt in rrule(freq=MONTHLY, dtstart=start_month, until=month_for):
        last_day_of_month= calendar.monthrange(dt.year, dt.month)[1]
        yield (dt.year, dt.month, last_day_of_month)
        #yield (dt.year, dt.month, calendar.monthrange(dt.year, dt.month)[1])


# class TimeFrame(object):

#     def __init__(self, **kwargs):
#         '''

#         combination we need
#         * start and end datetime
#         * start
#         '''
#         self.start = kwargs.get('start')
#         self.end = kwargs.get('end')
#         self.duration = kwargs.get('duration')


#     @classmethod
#     def make_series(from_datetime, duration, reverse=False):
#         '''
#         Returns a list of
#         TODO: Create a class from this
#         '''
#         timeframes = []
#         if not reverse:
#             rrule_kwargs = dict(
#                 dtstart=as_datetime(from_datetime),
#             )
#             for dt in rrule(**rrule_kwargs):
#                 timeframes.append(TimeFrame(
#                     start=))
    #for dt in rrule(DAILY, dtstart=start_date, until=end_date):




