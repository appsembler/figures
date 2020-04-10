"""Backfills metrics models

Initially developed to support API performance improvements
"""

from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta

from django.utils.timezone import utc

from figures.mau import get_mau_from_student_modules
from figures.models import SiteMonthlyMetrics
from figures.sites import get_student_modules_for_site


def backfill_monthly_metrics_for_site(site, overwrite):
    """Quick hack function to backfill all historical site metrics for the site

    We are a bit verbose with the output to help testing and validation since
    this function was quickly put together
    """
    site_sm = get_student_modules_for_site(site)
    if not site_sm:
        return None

    first_created = site_sm.order_by('created').first().created

    # We do this because there _might_ be a bug in `dateutil.rrule`. It was
    # skipping over February when we used the `created` field directly for the
    # start_month variable
    start_month = datetime(year=first_created.year,
                           month=first_created.month,
                           day=1).replace(tzinfo=utc)
    last_month = datetime.utcnow().replace(tzinfo=utc) - relativedelta(months=1)
    backfilled = []
    for dt in rrule(freq=MONTHLY, dtstart=start_month, until=last_month):
        mau = get_mau_from_student_modules(student_modules=site_sm,
                                           year=dt.year,
                                           month=dt.month)
        month_sm = site_sm.filter(created__year=dt.year, created__month=dt.month)
        month_learners = month_sm.values_list('student__id', flat=True).distinct()

        obj, created = SiteMonthlyMetrics.add_month(
            site=site,
            year=dt.year,
            month=dt.month,
            active_user_count=month_learners.count(),
            overwrite=overwrite)

        backfill_rec = dict(
            obj=obj,
            created=created,
            dt=dt,
            mau=mau)
        backfilled.append(backfill_rec)

    return backfilled
