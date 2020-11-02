"""Calculates MAU data

Course MAU is the total count of unique active learners for the requested month

* Retrieves filtered StudentModule records from edx-platform
* Calculates MAU values for all courses (TBD filtering)
* Stores calculated values in Figures MAU metric models

The core functionality to process MAU data should be in this module.

See figures.tasks for the Celery tasks that run MAU jobs
"""

from __future__ import absolute_import
from figures.helpers import as_course_key
from figures.mau import get_mau_from_student_modules
from figures.models import CourseMauMetrics
from figures.sites import get_student_modules_for_course_in_site


def get_all_mau_for_site_course(site, courselike, month_for):
    """
    Extract a queryset of distinct MAU user ids for the site and course
    """
    sm_recs = get_student_modules_for_course_in_site(site,
                                                     as_course_key(courselike))
    mau_ids = get_mau_from_student_modules(student_modules=sm_recs,
                                           year=month_for.year,
                                           month=month_for.month)

    return mau_ids


def calculate_course_mau(mau_ids):
    """
    Returns the count of distinct MAU user ids

    Starting as a one liner function, purpose is to decouple each of the three
    ETL steps

    If we need to filter on staff add `courselike` argument and a kwarg for
    `filter_staff` and implement this function:
        ```
        def get_staff_for_course(courselike)
        ```

    Where `courselike` is an object that can return a unique course id

    Add conditional operation to filter out staff ids from the mau_ids queryset
    """
    return mau_ids.count()


def save_course_mau(site, courselike, month_for, mau_data, **kwargs):
    """
    Stores course MAU data into the Figures `CourseMauMetrics` model

    `mau_data` should be a dict: `dict(mau=mau_id_count)`

    """
    overwrite = kwargs.get('overwrite', False)

    obj, created = CourseMauMetrics.save_metrics(
        site=site,
        course_id=str(as_course_key(courselike)),
        date_for=month_for,
        data=mau_data,
        overwrite=overwrite)

    return obj, created


def collect_course_mau(site, courselike, month_for, **kwargs):
    """
    Extracts, transforms, loads course MAU data

    """
    overwrite = kwargs.get('overwrite', False)
    mau_ids = get_all_mau_for_site_course(site=site,
                                          courselike=courselike,
                                          month_for=month_for)
    mau_id_count = calculate_course_mau(mau_ids)
    mau_data = dict(mau=mau_id_count)
    obj, created = save_course_mau(site=site,
                                   courselike=courselike,
                                   month_for=month_for,
                                   mau_data=mau_data,
                                   overwrite=overwrite)

    return obj, created
