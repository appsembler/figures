
from django.db import models
from django.contrib.auth.models import User

from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

#from openedx.core.djangoapps.xmodule_django.models import BlockTypeKeyField, CourseKeyField, LocationKeyField

class StudentModule(models.Model):
    '''
    We're populating only the fields we need to run tests
    '''
    course_id = CourseKeyField(max_length=255, db_index=True)
    student = models.ForeignKey(User, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)