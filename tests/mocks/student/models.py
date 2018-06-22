

from django.db import models
from django.contrib.auth.models import User

from django_countries.fields import CountryField

from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

class UserProfile(models.Model):
    '''
    The production model is student.models.UserProfile
    '''
    user = models.OneToOneField(User, unique=True, db_index=True, related_name='profile')
    name = models.CharField(blank=True, max_length=255, db_index=True)
    country = CountryField(blank=True, null=True)


class CourseEnrollment(models.Model):
    '''
    The production model is student.models.CourseEnrollment

    The purpose of this mock is to provide the model needed to
    retrieve:
    * The learners enrolled in a course
    * When a learner enrolled
    * If the learner is active
    '''

    user = models.ForeignKey(User)
    course_id = CourseKeyField(max_length=255, db_index=True)
    created = models.DateTimeField(auto_now_add=True, null=True, db_index=True)

    # If is_active is False, then the student is not considered to be enrolled
    # in the course (is_enrolled() will return False)
    is_active = models.BooleanField(default=True)

    class Meta(object):
        unique_together = (('user', 'course_id'),)
        ordering = ('user', 'course_id')


class CourseAccessRole(models.Model):
    user = models.ForeignKey(User)
    # blank org is for global group based roles such as course creator (may be deprecated)
    org = models.CharField(max_length=64, db_index=True, blank=True)
    # blank course_id implies org wide role
    course_id = CourseKeyField(max_length=255, db_index=True, blank=True)
    role = models.CharField(max_length=64, db_index=True)

    class Meta(object):
        unique_together = ('user', 'org', 'course_id', 'role')

    @property
    def _key(self):
        """
        convenience function to make eq overrides easier and clearer. arbitrary decision
        that role is primary, followed by org, course, and then user
        """
        return (self.role, self.org, self.course_id, self.user_id)

    def __eq__(self, other):
        """
        Overriding eq b/c the django impl relies on the primary key which requires fetch. sometimes we
        just want to compare roles w/o doing another fetch.
        """
        return type(self) == type(other) and self._key == other._key  # pylint: disable=protected-access

    def __hash__(self):
        return hash(self._key)

    def __lt__(self, other):
        """
        Lexigraphic sort
        """
        return self._key < other._key  # pylint: disable=protected-access

    def __unicode__(self):
        return "[CourseAccessRole] user: {}   role: {}   org: {}   course: {}".format(self.user.username, self.role, self.org, self.course_id)
