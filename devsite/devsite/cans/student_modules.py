
from __future__ import absolute_import
from django.contrib.auth import get_user_model

from figures.compat import StudentModule

from figures.helpers import as_course_key, as_datetime

# Yes, this is empty. Need to decide if we're going to do hardcoded canned data
STUDENT_MODULE_DATA = [

]


def seed_student_modules_fixed(data=None):
    '''
    '''
    if not data:
        data = STUDENT_MODULE_DATA
    for rec in data:
        StudentModule.objects.update_or_create(
            student=get_user_model().objects.get(username=rec['username']),
            course_id=as_course_key(rec['course_id']),
            create=as_datetime(rec['created']),
            modified=as_datetime(rec['modified']),
        )
