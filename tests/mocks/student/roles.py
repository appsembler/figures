'''
Mocks role classes needed in Figures tests
'''


class MockCourseRole(object):
    '''
    For initial mocking, return empty list for the 'users_with_role' call
    '''
    def __init__(self, role, course_key):
        self.role = role
        self.course_key = course_key

    def users_with_role(self):
        return []

class CourseCcxCoachRole(MockCourseRole):
    ROLE = 'ccx_coach'

    def __init__(self, *args, **kwargs):
        super(CourseCcxCoachRole, self).__init__(self.ROLE, *args, **kwargs)


class CourseInstructorRole(MockCourseRole):
    ROLE = 'instructor'

    def __init__(self, *args, **kwargs):
        super(CourseInstructorRole, self).__init__(self.ROLE, *args, **kwargs)


class CourseStaffRole(MockCourseRole):
    ROLE = 'staff'

    def __init__(self, *args, **kwargs):
        super(CourseStaffRole, self).__init__(self.ROLE, *args, **kwargs)
