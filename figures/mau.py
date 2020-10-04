"""
This module provides MAU metrics retrieval functionality
"""

from __future__ import absolute_import
from datetime import datetime, timedelta
from django.utils.timezone import utc

from figures.compat import RELEASE_LINE

from figures.models import CourseMauMetrics, SiteMauMetrics
from figures.sites import (
    get_course_keys_for_site,
    get_student_modules_for_site,
    get_student_modules_for_course_in_site,
)


def get_mau_from_student_modules(student_modules, year, month):
    """
    Return records modified in year and month

    Inspect StudentModule records to see if modified is set to created date
    when records are created. If so, then we can just get the modified date in
    the specified month

    """
    qs = student_modules.filter(modified__year=year,
                                modified__month=month)
    return qs.values_list('student__id', flat=True).distinct()


def get_mau_from_site_course(site, course_id, year, month):
    """Convenience function to get the distinct active users for a given course
    in a site

    """
    student_modules = get_student_modules_for_course_in_site(site=site,
                                                             course_id=course_id)
    return get_mau_from_student_modules(student_modules=student_modules,
                                        year=year,
                                        month=month)


def retrieve_live_site_mau_data(site):
    """
    Used this when we need to retrieve unique active users for the
    whole site
    """
    student_modules = get_student_modules_for_site(site)
    today = datetime.utcnow()
    users = get_mau_from_student_modules(student_modules=student_modules,
                                         year=today.year,
                                         month=today.month)
    return dict(
        count=users.count(),
        month_for=today.date(),
        domain=site.domain,
    )


def retrieve_live_course_mau_data(site, course_id):
    """
    Used this when we need to retrieve unique active users for a given course
    in the site
    """
    student_modules = get_student_modules_for_course_in_site(site, course_id)
    today = datetime.utcnow()
    users = get_mau_from_student_modules(student_modules=student_modules,
                                         year=today.year,
                                         month=today.month)
    return dict(
        count=users.count(),
        month_for=today.date(),
        course_id=str(course_id),
        domain=site.domain,
    )


def mau_1g_for_month_as_of_day(sm_queryset, date_for):
    """Get the MAU from the sm, as of the "date_for" for "date_for" month

    sm_queryset is the StudentModule queryset for our source

    This is a MAU 1G function that calculates the monthly active users as of the
    day in the given month.

    This function queries `courseware.models.StudentModule` to identify users
    who are active in the site

    Retrieves records based on date of the `StudentModule.modified` field
    Returns a queryset of distinct user ids
    """

    # TODO: Remove this `if` branch after dropping Ginkgo support.
    if RELEASE_LINE == 'ginkgo':
        # Django 1.8 appears not to support 'lte' on the 'day' of a datetime
        # Therefore we have to get records within a range
        start_date = datetime(year=date_for.year,
                              month=date_for.month,
                              day=1).replace(tzinfo=utc)
        # We do this in case 'date_for' is at the end of the month and get
        # the 'day_after' as midnight of the next day so we can use '__lt'. If
        # we simply used '__lte', then we exclude any events that happened on
        # the 'date_for' in hours after the 'date_for' hours.

        # temporary var as we don't know
        day_after_temp = date_for + timedelta(days=1)
        day_after = datetime(year=day_after_temp.year,
                             month=day_after_temp.month,
                             day=day_after_temp.day).replace(tzinfo=utc)

        # We don't use 'dict(modified__range=[start_date, date_for])' because
        # doing "__lt" for 0:00 hour tne next day means we don't have to worry
        # about fractions of a second on the last second of the last day
        filter_args = dict(modified__gte=start_date, modified__lt=day_after)
    else:
        filter_args = dict(modified__year=date_for.year,
                           modified__month=date_for.month,
                           modified__day__lte=date_for.day)

    month_sm = sm_queryset.filter(**filter_args)
    return month_sm.values('student__id').distinct()


def site_mau_1g_for_month_as_of_day(site, date_for):
    """Get the MAU for the given site, as of the "date_for" in the month

    This is a conenvience function. It gets the student modules for the site,
    then calls

        `figures.mau.mau_for_month_as_of_day(...)`

    Returns a queryset with distinct user ids
    """
    site_sm = get_student_modules_for_site(site)
    return mau_1g_for_month_as_of_day(sm_queryset=site_sm,
                                      date_for=date_for)


def store_mau_metrics(site, overwrite=False):
    """
    Save "snapshot" of MAU metrics
    """
    today = datetime.utcnow()

    # get site data
    student_modules = get_student_modules_for_site(site)
    site_mau = get_mau_from_student_modules(student_modules=student_modules,
                                            year=today.year,
                                            month=today.month)

    # store site data
    site_mau_obj, _created = SiteMauMetrics.save_metrics(site=site,
                                                         date_for=today.date(),
                                                         data=dict(mau=site_mau.count()),
                                                         overwrite=overwrite)
    course_mau_objects = []
    for course_key in get_course_keys_for_site(site):
        course_student_modules = student_modules.filter(course_id=course_key)
        course_mau = get_mau_from_student_modules(
            student_modules=course_student_modules,
            year=today.year,
            month=today.month)
        course_mau_obj, _created = CourseMauMetrics.save_metrics(
                site=site,
                course_id=str(course_key),
                date_for=today.date(),
                data=dict(mau=course_mau.count()),
                overwrite=overwrite)

        course_mau_objects.append(course_mau_obj)

    return dict(smo=site_mau_obj,
                cmos=course_mau_objects)
