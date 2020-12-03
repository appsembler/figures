'''Figures compatability module

This module serves to provide a common access point to functionality that
differs from  different named Open edX releases

We can identify the Open edX named release for Ginkgo and later by getting the
value from openedx.core.release.RELEASE_LINE. This will be the release name as
a lowercase string, such as 'ginkgo' or 'hawthorn'

'''
# pylint: disable=ungrouped-imports,useless-suppression

from __future__ import absolute_import


class UnsuportedOpenedXRelease(Exception):
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


def course_grade(learner, course):
    """
    Compatibility function to retrieve course grades

    Returns the course grade for the specified learner and course
    """
    if RELEASE_LINE == 'ginkgo':
        return CourseGradeFactory().create(learner, course)
    else:  # Assume Hawthorn or greater
        return CourseGradeFactory().read(learner, course)


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
