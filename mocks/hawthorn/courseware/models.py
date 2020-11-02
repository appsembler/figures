
from __future__ import absolute_import
from django.db import models
from django.contrib.auth.models import User

from openedx.core.djangoapps.xmodule_django.models import (
    CourseKeyField,
    #! LocationKeyField,
    )


class StudentModule(models.Model):
    '''Mocks the courseware.models.StudentModule

    class attributes declared in StudentModule but not yet
    needed for mocking are remarked out with a '#!'
    They are here to
    A) Help understand context of the class without requiring opening the
       courseware/models.py file
    B) Be available to quickly update this mock when needed
    '''
    #! MODEL_TAGS = ['course_id', 'module_type']

    # For a homework problem, contains a JSON
    # object consisting of state
    #! MODULE_TYPES = (('problem', 'problem'),
    #!                 ('video', 'video'),
    #!                 ('html', 'html'),
    #!                 ('course', 'course'),
    #!                 ('chapter', 'Section'),
    #!                 ('sequential', 'Subsection'),
    #!                 ('library_content', 'Library Content'))

    #! module_state_key = LocationKeyField(max_length=255, db_index=True, db_column='module_id')

    student = models.ForeignKey(User, db_index=True)

    course_id = CourseKeyField(max_length=255, db_index=True)

    #! class Meta(object):
    #!     app_label = "courseware"
    #!     unique_together = (('student', 'module_state_key', 'course_id'),)

    #! # Internal state of the object
    #! state = models.TextField(null=True, blank=True)

    #! # Grade, and are we done?
    #! grade = models.FloatField(null=True, blank=True, db_index=True)
    #! max_grade = models.FloatField(null=True, blank=True)
    #! DONE_TYPES = (
    #!     ('na', 'NOT_APPLICABLE'),
    #!     ('f', 'FINISHED'),
    #!     ('i', 'INCOMPLETE'),
    #!  )
    #! done = models.CharField(max_length=8, choices=DONE_TYPES, default='na', db_index=True)

    # the production model sets 'auto_now_add=True' andn 'db_index=True'
    created = models.DateTimeField()
    modified = models.DateTimeField()
