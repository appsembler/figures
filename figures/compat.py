'''Figures compatability module

This module serves to provide a common access point to functionality that
differs from  different named Open edX releases

We can identify the Open edX named release for Ginkgo and later by getting the
value from openedx.core.release.RELEASE_LINE. This will be the release name as
a lowercase string, such as 'ginkgo' or 'hawthorn'

'''
# pylint: disable=ungrouped-imports,useless-suppression

try:
    from openedx.core.release import RELEASE_LINE
except ImportError:
    # we are pre-ginkgo
    RELEASE_LINE = None

try:
    # First try to import for the path as of hawthorn
    from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
except ImportError:
    try:
        # Next try to import for the path as of ginkgo
        from lms.djangoapps.grades.new.course_grade_factory import CourseGradeFactory
    except ImportError:
        # try the pre-ginkgo path
        from lms.djangoapps.grades.new.course_grade import CourseGradeFactory    # noqa: F401


if RELEASE_LINE == 'ginkgo':
    from certificates.models import GeneratedCertificate  # noqa pylint: disable=unused-import,import-error
else:
    from lms.djangoapps.certificates.models import GeneratedCertificate  # noqa pylint: disable=unused-import,import-error


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
        return chapter_grades.values()
    elif isinstance(chapter_grades, list):
        return chapter_grades
    else:
        # TODO: improve clarity, add a message
        # This may be what
        raise TypeError
