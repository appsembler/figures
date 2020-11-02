"""Populate Figures site monthly metrics data

"""

from __future__ import absolute_import
from datetime import datetime
from django.utils.timezone import utc
from dateutil.relativedelta import relativedelta

from figures.models import SiteMonthlyMetrics
from figures.sites import get_student_modules_for_site


def fill_month(site, month_for, student_modules=None, overwrite=False):
    """Fill a month's site monthly metrics for the specified site
    """
    if not student_modules:
        student_modules = get_student_modules_for_site(site)

    if student_modules:
        month_sm = student_modules.filter(modified__year=month_for.year,
                                          modified__month=month_for.month)
        mau_count = month_sm.values_list('student_id',
                                         flat=True).distinct().count()
    else:
        mau_count = 0

    obj, created = SiteMonthlyMetrics.add_month(site=site,
                                                year=month_for.year,
                                                month=month_for.month,
                                                active_user_count=mau_count,
                                                overwrite=overwrite)
    return obj, created


def fill_last_month(site, overwrite=False):
    """Convenience function to fill previous month's site monthly metrics
    """
    # Maybe we want to make 'last_month' a 'figures.helpers' method
    last_month = datetime.utcnow().replace(tzinfo=utc) - relativedelta(months=1)
    return fill_month(site=site, month_for=last_month, overwrite=overwrite)
