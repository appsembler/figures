'''Figures compatability module

This module serves to provide a common access point to functionality that
differs from  different named Open edX releases

We can identify the Open edX named release for Ginkgo and later by getting the
value from openedx.core.release.RELEASE_LINE. This will be the release name as
a lowercase string, such as 'ginkgo' or 'hawthorn'

'''

try:
    from openedx.core.release import RELEASE_LINE
except ImportError:
    # we are pre-ginkgo
    RELEASE_LINE = None

try:
    # First try to import for ginkgo and onward
    from lms.djangoapps.grades.new.course_grade_factory import CourseGradeFactory
except ImportError:
    # try the old (pre-ginkgo) location
    from lms.djangoapps.grades.new.course_grade import CourseGradeFactory    # noqa: F401


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
        raise TypeError
