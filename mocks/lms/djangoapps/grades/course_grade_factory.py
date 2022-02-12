

from __future__ import absolute_import
from lms.djangoapps.grades.course_grade import CourseGrade


class MockCourseData(object):

    def __init__(self, user, course=None, collected_block_structure=None, structure=None, course_key=None):
        if not any([course, collected_block_structure, structure, course_key]):
            raise ValueError(
                "You must specify one of course, collected_block_structure, structure, or course_key to this method."
            )
        self.user = user
        self._collected_block_structure = collected_block_structure
        self._structure = structure
        self._course = course
        self._course_key = course_key
        self._location = None


class CourseGradeFactory(object):

    def read(
        self,
        user,
        course=None,
        collected_block_structure=None,
        course_structure=None,
        course_key=None
    ):
        course_data = MockCourseData(
            user, course, collected_block_structure, course_structure, course_key)
        return CourseGrade(
            user,
            course_data,
            force_update_subsections=False
        )
