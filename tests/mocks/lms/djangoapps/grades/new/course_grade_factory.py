

from .course_grade import CourseGrade

class CourseGradeFactory(object):


    def create(self, user, course=None, collected_block_structure=None, course_structure=None, course_key=None):
        return CourseGrade(user=user,course=course,course_key=course_key)
