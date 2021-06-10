"""Helper functions to make data handling and conversions easier

# Figures 0.3.13 - Defining scope of this module

The purpose of this module is to provide conveniece methods around commonly
executed statements. These convenience methods should serve as shorthand for
code we would repeatedly execute which don't yet have a module of their own.

The idea is that if there is not yet a module for some helper function, we put
it in here until we see a pattern. We then either identify a new module and
transplate these like functions out of this module into the new one. Or we
identify that functions in here actually should go in an existing module.

The purposes for this are:

1. Reduce development time cost by not having to stop and design (informally or
   formally) a new module or inspect all the existing modules to find an
   appropriate home. The second point is helpful for those not intimately
   familiar with the Figures codebase

2. Avoid premature optimization in building out new module functionality because
   we are adding a single method (Avoid the desire to fill this new module with
   more than the new functionality that serves our immediate needs)

3. Avoid over specificifity, which can results in an explosion of tiny modules
   that may be too specific in their context


## Background

Originally this module served as a variant of a 'utils' module, but with the
express purpose of providing convenience "helper" functions to help DRY (do not
repeat yourself) the code and make the code more readable

## What does not belong here?

* "Feature" functionality does not belong here
* Long functions do not belong here
* Code that communicates outside of Figures does not belong here. No database,
  filesystem, or network connectiviely functionality belongs here

This is not an exhaustive list. We'll grow it as needed.

An important point is that we should not expect this module to be a permanent
home for functionality.
"""

from __future__ import absolute_import
import calendar
import datetime
from importlib import import_module
from django.conf import settings
from django.utils.timezone import utc

from dateutil.parser import parse as dateutil_parse
from dateutil.relativedelta import relativedelta

from opaque_keys.edx.keys import CourseKey
import six


def is_multisite():
    """
    A naive but reliable check on whether Open edX is using multi-site setup or not.

    Override by setting ``FIGURES_IS_MULTISITE`` to true in the Open edX FEATURES.

    TODO: Move to `figures.sites`
    """
    return bool(settings.FEATURES.get('FIGURES_IS_MULTISITE', False))


def log_pipeline_errors_to_db():
    """
    Capture pipeline errors to the figures.models.PipelineError model.

    Override by setting ``FIGURES_LOG_PIPELINE_ERRORS_TO_DB`` to false in the Open edX FEATURES.

    TODO: This is an environment/setting "getter". Should be moved to `figures.settings`
    """
    return bool(settings.FEATURES.get('FIGURES_LOG_PIPELINE_ERRORS_TO_DB', True))


def import_from_path(path):
    """
    Import a function or class from a its string Python path.

    Note: This help does _not_ attempt to handle exceptions well.
      Instead it throws them as is. The rationale is that such exceptions are
      only fixable at the deploy time and attempting to handle such errors
      would risk hiding the errors and making it more difficult to fix.

    :param path: string path in the format "module.submodule:variable".
    :return object
    """
    module_path, variable_name = path.split(':', 1)
    module = import_module(module_path)
    return getattr(module, variable_name)


def as_course_key(course_id):
    """Returns course id as a CourseKey instance

    Convenience method to return the paramater unchanged if it is of type
    ``CourseKey`` or attempts to convert to ``CourseKey`` if of type str or
    unicode.

    Raises TypeError if an unsupported type is provided

    NOTE: This is a good example of a helper method that belongs here
    """
    if isinstance(course_id, CourseKey):
        return course_id
    elif isinstance(course_id, six.string_types):  # noqa: F821
        return CourseKey.from_string(course_id)
    else:
        raise TypeError('Unable to convert course id with type "{}"'.format(
            type(course_id)))


def as_datetime(val):
    '''
    TODO: Add arg flag to say if caller wants end of day, beginning of day
    or a particular time of day if the param is a datetime.date obj


    NOTE: The date functions here could be in a `figures.datetools` module.

    Not set on the name `datetools` but some date specific module
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

    elif isinstance(val, six.string_types):  # noqa: F821
        return dateutil_parse(val).replace(tzinfo=utc)
    else:
        raise TypeError(
            'value of type "{}" cannot be converted to a datetime object'.format(
                type(val)))


def as_date(val):
    """Casts the value to a ``datetime.date`` object if possible

    Else raises ``TypeError``

    NOTE: This is a good example of a helper method that belongs here
          We could also move this and the other date helpers to a "date"
          labeled module in Figures. Then at some future time, move those out
          into a "toolbox" package to abstrac
    """
    # Important to check if datetime first because datetime.date objects
    # pass the isinstance(obj, datetime.date) test
    if isinstance(val, datetime.datetime):
        return val.date()
    elif isinstance(val, datetime.date):
        return val
    elif isinstance(val, six.string_types):  # noqa: F821
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


def days_in_month(month_for):
    _, num_days_in_month = calendar.monthrange(month_for.year, month_for.month)
    return num_days_in_month


# TODO: Consider changing name to 'months_back_iterator' or similar
def previous_months_iterator(month_for, months_back):
    """Iterator returns a year,month tuple for n months including the month_for.
    months_back is a misnomer as iteration includes the start month.  The actual
    number of previous months iterated is months_back minus one.

    month_for is either a date, datetime, or tuple with year and month
    months back is the number of months to iterate
    """

    if isinstance(month_for, tuple):
        # TODO make sure we've got just two values in the tuple
        month_for = datetime.date(year=month_for[0], month=month_for[1], day=1)
    if isinstance(month_for, (datetime.datetime, datetime.date)):
        start_month = month_for - relativedelta(months=(max(0, months_back - 1)))

    for n_months in range(max(1, months_back)):
        dt = start_month + relativedelta(months=n_months)
        last_day_of_month = days_in_month(month_for=dt)
        yield (dt.year, dt.month, last_day_of_month)


def first_last_days_for_month(month_for):
    """Given a MM/YYYY string, derive the first and last days for the month

    Returns a tuple of first_day, last_day
    """
    month, year = [int(val) for val in month_for.split('/')]
    first_day = datetime.date(year=year,
                              month=month,
                              day=1)
    last_day = datetime.date(year=year,
                             month=month,
                             day=days_in_month(first_day))
    return first_day, last_day
