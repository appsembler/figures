"""Populate Figures site monthly metrics data

"""

from __future__ import absolute_import
from datetime import datetime
from django.db import connection
from django.db.models import IntegerField
from django.utils.timezone import utc
from dateutil.relativedelta import relativedelta

from figures.compat import RELEASE_LINE
from figures.models import SiteMonthlyMetrics
from figures.sites import get_student_modules_for_site


def _get_fill_month_raw_sql_for_month(site_ids, month_for):
    """Return a string for the raw SQL statement to get distinct student_id counts.
    """
    # this is just a separate function so it can be patched in test to acccommodate sqlite
    return """\
    SELECT COUNT(DISTINCT student_id) from courseware_studentmodule
    where id in {}
    and MONTH(modified) = {}
    and YEAR(modified) = {}
    """.format(site_ids, month_for.month, month_for.year)


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
            if RELEASE_LINE == 'ginkgo':
                site_ids = tuple(
                    [int(sid) for sid in student_modules.values_list('id', flat=True).distinct()]
                )
            else:
                # make sure we get integers and not longints from db
                from django.db.models.functions import Cast
                site_ids = tuple(
                    student_modules.annotate(
                        id_as_int=Cast('id', IntegerField())
                    ).values_list('id_as_int', flat=True).distinct()
                )

            statement = _get_fill_month_raw_sql_for_month(site_ids, month_for)
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
