'''
Provides fake models for openedx.core.djangoapps.content.course_overviews

Overview
--------

The purpose of this module is to provide the minimum models in order to mock
Figures access to edx-platform models

Reference
---------

See also the lms.djangoapps.course_api.serializers.CourseSerializer class

This provides the data that are returned in the built-in edx-platform
course_api REST API calls

Future
------

If and when openedx.core is re-architected to be independent from edx-platform,
or we can selectively include apps from edx-platform without requiring complex
test settings and a filesystem based test infrastructure, then we can revisit
removing these mocks

'''

from __future__ import absolute_import
from django.db import models

from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

class CourseOverview(models.Model):
    '''
    Provides a mock model for the edx-platform 'CourseOverview' model

    Future Improvements
    -------------------

    We want to provide enhanced live querying like
    - "Which courses are invitation only?"
    - "Which courses have a maximum allowed enrollment above X"
    
    '''
    # Faking id, picking arbitrary length
    # Actual field is of type opaque_keys.edx.keys.CourseKey
    #id = models.CharField(db_index=True, primary_key=True, max_length=255)
    id = CourseKeyField(db_index=True, primary_key=True, max_length=255)
    display_name = models.TextField(null=True)
    org = models.TextField(max_length=255, default='outdated_entry')
    # For the tests, the CourseOverviewFactory does a LazyAttribute on
    # display_org_with_default
    display_org_with_default = models.TextField()
    number = models.TextField()
    created = models.DateTimeField(null=True) # from TimeStampedModel
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    enrollment_start = models.DateTimeField(null=True)
    enrollment_end = models.DateTimeField(null=True)
    self_paced = models.BooleanField(default=False)

    @property
    def display_name_with_default_escaped(self):
        return self.display_name

    @property
    def display_number_with_default(self):
        return self.number

    @property
    def display_order_with_default(self):
        return self.org

    @classmethod
    def get_from_id(cls, course_id):
        return CourseOverview.objects.get(id=course_id)
