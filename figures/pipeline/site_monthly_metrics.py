"""Populate Figures site monthly metrics data

"""

from __future__ import absolute_import
from datetime import datetime
from django.db import connection
from django.utils.timezone import utc
from dateutil.relativedelta import relativedelta

from figures.models import SiteMonthlyMetrics
from figures.sites import get_student_modules_for_site


def fill_month(site, month_for, student_modules=None, overwrite=False, use_raw=False):
    """Fill a month's site monthly metrics for the specified site
    """
    if not student_modules:
        student_modules = get_student_modules_for_site(site)

    if student_modules:
        if not use_raw:
            month_sm = student_modules.filter(modified__year=month_for.year,
                                              modified__month=month_for.month)
            mau_count = month_sm.values_list('student_id',
                                             flat=True).distinct().count()
        else:
            site_ids = tuple(student_modules.values_list('id', flat=True).distinct())
            year = month_for.year
            if (connection.vendor == 'sqlite'):  # for tests, ugh. suggestions welcome  :/
                month = str(month_for.month).zfill(2)
                statement = """\
                SELECT COUNT(DISTINCT student_id) from courseware_studentmodule
                where id in {}
                and strftime('%m', datetime(modified)) = '{}'
                and strftime('%Y', datetime(modified)) = '{}'
                """.format(site_ids, month, year)
            else:
                month = month_for.month
                statement = """\
                SELECT COUNT(DISTINCT student_id) from courseware_studentmodule
                where id in {}
                and MONTH(modified) = {}
                and YEAR(modified) = {}
                """.format(site_ids, month, year)

            with connection.cursor() as cursor:
                cursor.execute(statement)
                row = cursor.fetchone()
                mau_count = row[0]
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
