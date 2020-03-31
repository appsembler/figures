"""
This module provides MAU metrics retrieval functionality
"""

from datetime import datetime

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
