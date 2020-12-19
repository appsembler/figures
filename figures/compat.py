"""Figures compatability module

This module serves to provide a common access point to edx-platform objects.

It was originally intended to encapsulate functionality that differs from
different named Open edX releases

We can identify the Open edX named release for Ginkgo and later by getting the
value from openedx.core.release.RELEASE_LINE. This will be the release name as
a lowercase string, such as 'ginkgo' or 'hawthorn'

TODO: Consider wrapping edx-platform's `get_course_by_id` in a function as it
      raises a django.http.Http404 if the course if not found, which is weird.
      We can then raise our own `CourseNotFound` which makes exception handling
      in Figures clearer to handle with a specific exception. Our callers could
      do the following:
      ```
      try:
          return get_course_by_id(id)
      except CourseNotFound:
          handle exception
      ```
"""
# pylint: disable=ungrouped-imports,useless-suppression,wrong-import-position

from __future__ import absolute_import
from django.http import Http404
from figures.helpers import as_course_key


class UnsuportedOpenedXRelease(Exception):
    pass


class CourseNotFound(Exception):
    """Raised when edx-platform 'course' structure is not found
    """
    pass


# Pre-Ginkgo does not define `RELEASE_LINE`
try:
    from openedx.core.release import RELEASE_LINE
except ImportError:
    raise UnsuportedOpenedXRelease(
        'Unidentified Open edX release: '
        'figures.compat could not import openedx.core.release.RELEASE_LINE')


if RELEASE_LINE == 'ginkgo':
    from lms.djangoapps.grades.new.course_grade_factory import CourseGradeFactory  # noqa pylint: disable=unused-import,import-error
else:  # Assume Hawthorn or greater
    from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory  # noqa pylint: disable=unused-import,import-error

if RELEASE_LINE == 'ginkgo':
    from certificates.models import GeneratedCertificate  # noqa pylint: disable=unused-import,import-error
else:  # Assume Hawthorn or greater
    from lms.djangoapps.certificates.models import GeneratedCertificate  # noqa pylint: disable=unused-import,import-error

if RELEASE_LINE in ['ginkgo', 'hawthorn']:
    from courseware.models import StudentModule  # noqa pylint: disable=unused-import,import-error
else:  # Assume Juniper or greater
    from lms.djangoapps.courseware.models import StudentModule  # noqa pylint: disable=unused-import,import-error

if RELEASE_LINE in ['ginkgo', 'hawthorn']:
    from courseware.courses import get_course_by_id  # noqa pylint: disable=unused-import,import-error
else:  # Assume Juniper or greater
    from lms.djangoapps.courseware.courses import get_course_by_id  # noqa pylint: disable=unused-import,import-error

if RELEASE_LINE == 'ginkgo':
    from openedx.core.djangoapps.xmodule_django.models import CourseKeyField  # noqa pylint: disable=unused-import,import-error
else:  # Assume Hawthorn or greater
    from opaque_keys.edx.django.models import CourseKeyField  # noqa pylint: disable=unused-import,import-error


# preemptive addition. Added it here to avoid adding to figures.models
# In fact, we should probably do a refactoring that makes all Figures import it
# from here
from student.models import CourseAccessRole, CourseEnrollment  # noqa pylint: disable=unused-import,import-error
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview  # noqa pylint: disable=unused-import,import-error


def course_grade(learner, course):
    """
    Compatibility function to retrieve course grades

    Returns the course grade for the specified learner and course
    """
    if RELEASE_LINE == 'ginkgo':
        return CourseGradeFactory().create(learner, course)
    else:  # Assume Hawthorn or greater
        return CourseGradeFactory().read(learner, course)


def course_grade_from_course_id(learner, course_id):
    """Get the edx-platform's course grade for this enrollment

    IMPORTANT: Do not use in API calls as this is an expensive operation.
    Only use in async or pipeline.

    We handle the exception so that we return a specific `CourseNotFound`
    instead of the non-specific `Http404`
    edx-platform `get_course_by_id` function raises a generic `Http404` if it
    cannot find a course in modulestore. We trap this and raise our own
    `CourseNotFound` exception as it is more specific.

    TODO: Consider optional kwarg param or Figures setting to log performance.
          Bonus points: Make id a decorator
    """
    try:
        course = get_course_by_id(course_key=as_course_key(course_id))
    except Http404:
        raise CourseNotFound('{}'.format(str(course_id)))
    course._field_data_cache = {}  # pylint: disable=protected-access
    course.set_grading_policy(course.grading_policy)
    return course_grade(learner, course)


def chapter_grade_values(chapter_grades):
    '''

    Ginkgo introduced ``BlockUsageLocator``into the ``chapter_grades`` collection


    For the current functionality we need, we can simply check if chapter_grades
    acts as a list or a dict
    '''

    if isinstance(chapter_grades, dict):
        return list(chapter_grades.values())
    elif isinstance(chapter_grades, list):
        return chapter_grades
    else:
        # TODO: improve clarity, add a message
        # This may be what
        raise TypeError
