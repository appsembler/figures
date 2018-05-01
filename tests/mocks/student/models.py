

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
