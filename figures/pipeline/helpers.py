"""Helper module specific to Figures pipeline

The code in this module is intended specifically to run in Figures pipeline
without consideration of running elsewhere, such as Figures API calls.
"""

from datetime import datetime
from django.utils.timezone import utc
from figures.helpers import as_date, prev_day


class DateForCannotBeFutureError(Exception):
    """Raise this if a future date is requested for pipeline processing
    """
    pass


def pipeline_date_for_rule(date_for):
    """Common logic to assign the 'date_for' date for daily pipeline processing

    * If 'date_for' is 'None' or today, then this function returns a
      'datetime.date' instance for yesterday
    * If 'date_for' is a date in the past, this function returns the
      'datetime.date' representation of the date
    * If 'date_for' is in the future, then `DateForCannotBeFutureError` is
      raised

    As part of normal Figures data collection, the pipeline must collect data
    from the previous calendar day, assuming all timestamps are UTC.
    This is to build a complete picture of a 24 hour period.

    This function exists to have this logic in a single place in the code.
    This logic is specific to the pipeline so it belongs in Figures' pipeline
    namespce.

    We may rework this as a decorator or as part of core functionality in a
    base class from which daily metrics classes can derive.
    """
    today = datetime.utcnow().replace(tzinfo=utc).date()
    if not date_for:
        date_for = prev_day(today)
    else:
        # Because we are working on the calendar day and the daily metrics
        # models use date and not datetime for the 'date_for' fields
        date_for = as_date(date_for)

        # Either we are backfilling data (if the date is prior to yesterday)
        # or the caller explicity requests to process for yesterday
        if date_for > today:
            msg = 'Attempted pipeline call with future date: "{date_for}"'
            raise DateForCannotBeFutureError(msg.format(date_for=date_for))
        elif date_for == today:
            return prev_day(today)

    return date_for
