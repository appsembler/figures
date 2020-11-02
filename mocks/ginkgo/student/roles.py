'''
Mocks role classes needed in Figures tests
'''

from __future__ import absolute_import
from django.contrib.auth.models import User

from openedx.core.djangoapps.xmodule_django.models import CourseKeyField
from student.models import CourseAccessRole

class MockCourseRole(object):
    '''
    Mock student.models.CourseRole and its parent classes

    Guideline: only implement the minimum needed to simulate edx-platform for
    the Figures unit tests
    '''
    def __init__(self, role, course_key):

        # The following are declared in studen.roles.RoleBase
        self.org = ''
        self._role_name = role
        # The following are declared in student.roles.CourseRole
        self.role = role
        self.course_key = course_key

    def users_with_role(self):
        """
        Return a django QuerySet for all of the users with this role
        """
        # Org roles don't query by CourseKey, so use CourseKeyField.Empty for that query
        if self.course_key is None:
            self.course_key = CourseKeyField.Empty
        entries = User.objects.filter(
            courseaccessrole__role=self._role_name,
            courseaccessrole__org=self.org,
            courseaccessrole__course_id=self.course_key
        )
        return entries


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
