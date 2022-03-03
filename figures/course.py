"""Course specific module for Figures

## This module defined a `Course` class for data retrieval

Initialy created to do the following:

1. Reduce duplication in Figures "pipeline"
2. Build stronger course context to make Figures programming easier

## Background summary

A course id is globally unique as it has the identify of the organization and
organizations are globally unique.

## Design to think about - Enrollment class

Build on Django's lazy eval for querysets to create also an `Enrollment` class
that provides interfaces for `enrollment.date_for` and abstracts this bit of
mess that enrollments and student modules do NOT associate and instead we need
to query back and forth with `user_id` and `course_id`.
"""
from __future__ import absolute_import
from django.db.models import Q
from figures.compat import CourseEnrollment, StudentModule
from figures.helpers import (
    as_course_key,
    as_date,
)
from figures.sites import (
    get_site_for_course,
)


class Course(object):
    """Representation of a Course.

    The impetus for this class was dealing with querying for course enrollment
    and student module records for a specific course and for dates and date
    ranges for the course

    ## Architecture goal

    **Start simple and don't build the kitchen sink into here right away just
    because this class exists**

    ## Data under consideration to have this class handle

    * enrollments created on a date, before, after, between. However this would
    just be a convenience as the `.enrollments` property returns a queryset that
    can be filtered on `.created`
    """
    def __init__(self, course_id):
        """
        Initial version, we pass in a course ID and cast to a course key as an
        instance attribute. Later on, add `CourseLike` to abstract course identity
        so we can stop worrying about "Is it a string repretentation of a course or
        is it a CourseKey?"
        """
        self.course_key = as_course_key(course_id)

        # Improvement: Consider doing lazy evaluation
        self.site = get_site_for_course(self.course_id)

    def __repr__(self):
        return '{}.{} <{}>'.format(self.__module__,
                                   self.__class__.__name__,
                                   str(self.course_key))

    def __str__(self):
        return self.__repr__()

    @property
    def course_id(self):
        """Returns string representation of the course id
        """
        return str(self.course_key)

    @property
    def enrollments(self):
        """Returns CourseEnrollment queryset for the course
        """
        return CourseEnrollment.objects.filter(course_id=self.course_key)

    @property
    def student_modules(self):
        """Returns StudentModule queryset for enrollments in the course
        """
        return StudentModule.objects.filter(course_id=self.course_key)

    def student_modules_active_on_date(self, date_for):
        """Returns StudentModule queryset active on the date
        Active is if there was a `created` or `modified` field for the given date

        NOTE: We need to do this instead of simplly `modified__date=date_for`
        because we still have to support Django 1.8/Ginkgo
        """
        date_for = as_date(date_for)
        q_created = Q(created__year=date_for.year,
                      created__month=date_for.month,
                      created__day=date_for.day)
        q_modified = Q(modified__year=date_for.year,
                       modified__month=date_for.month,
                       modified__day=date_for.day)
        return self.student_modules.filter(q_created | q_modified)

    def enrollments_active_on_date(self, date_for):
        """Return CourseEnrollment queryset for enrollments active on the date

        Looks for student modules modified on the specified date and returns
        matching CourseEnrollment records
        """
        sm = self.student_modules_active_on_date(date_for)
        user_ids = sm.values('student_id').distinct()
        return CourseEnrollment.objects.filter(course_id=self.course_key,
                                               user_id__in=user_ids)
