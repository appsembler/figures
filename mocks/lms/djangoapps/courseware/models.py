from __future__ import absolute_import
from django.contrib.auth.models import User
from django.db import models

from opaque_keys.edx.django.models import \
    LearningContextKeyField  # ! LocationKeyField,


class StudentModule(models.Model):
    '''Mocks the courseware.models.StudentModule

    Keeps student state for a particular XBlock usage and particular student.
    Called Module since it was originally used for XModule state.

    class attributes declared in StudentModule but not yet
    needed for mocking are remarked out with a '#!'
    They are here to
    A) Help understand context of the class without requiring opening the
       courseware/models.py file
    B) Be available to quickly update this mock when needed
    '''
    #! objects = ChunkingManager()

    #! id = UnsignedBigIntAutoField(primary_key=True)  # pylint: disable=invalid-name

    ## The XBlock/XModule type (e.g. "problem")
    #! module_type = models.CharField(max_length=32, db_index=True)

    # Key used to share state. This is the XBlock usage_id
    #! module_state_key = LocationKeyField(max_length=255, db_index=True, db_column='module_id')
    # TODO: Review the most appropriate on_delete behaviour
    student = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)

    # The learning context of the usage_key (usually a course ID, but may be a library or something else)
    course_id = LearningContextKeyField(max_length=255, db_index=True)

    #! class Meta(object):
    #!     app_label = "courseware"
    #!     unique_together = (('student', 'module_state_key', 'course_id'),)

    #! # Internal state of the object
    #! state = models.TextField(null=True, blank=True)

    #! # Grade, and are we done?
    #! grade = models.FloatField(null=True, blank=True, db_index=True)
    #! max_grade = models.FloatField(null=True, blank=True)
    #! DONE_TYPES = (
    #!     (u'na', u'NOT_APPLICABLE'),
    #!     (u'f', u'FINISHED'),
    #!     (u'i', u'INCOMPLETE'),
    #!  )
    #! done = models.CharField(max_length=8, choices=DONE_TYPES, default='na', db_index=True)

    # the production model sets 'auto_now_add=True' andn 'db_index=True'
    created = models.DateTimeField()
    modified = models.DateTimeField()
