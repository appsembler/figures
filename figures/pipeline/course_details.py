'''
Module to get course details



Ref

See lms.djangoapps.course_structure_api
The endpoint for course structures
http://localhost:8000/api/course_structure/v0/course_structures/{course_id}}





from ..utils import get_course_outline_block_tree

./openedx/features/course_experience

openedx.features.course_experience.utils.get_course_outline_block_tree



--- Scratch ---

course_block_tree.keys()
['display_name', 'block_id', 'children', 'student_view_url', 'lms_web_url', 'type', 'id', 'graded', 'last_accessed']
(Pdb) course_block_tree['display_name']

'''

from django.http import HttpRequest

from courseware.courses import get_course_by_id
from lms.djangoapps.course_api.blocks.api import get_blocks

from openedx.core.djangoapps.content.course_structures.api.v0 import (
    api as cs_api,
    errors as cs_errors,
)
from openedx.features.course_experience.utils import get_course_outline_block_tree

from xmodule.modulestore.django import modulestore

from figures.helpers import as_course_key

def make_fake_http_request():
    request = HttpRequest()
    request.META['SERVER_NAME'] = 'fakehost'
    request.META['SERVER_PORT'] = 80
    request.user = None
    return request

class CourseStructure(object):
    '''
    See get_course_outline_block_tree(request, course_id) method in 
    openedx.features.course_experience.utils
    '''
    def __init__(self, course_id):
        self.depth=0
        self.course_key = as_course_key(course_id)
        self.course_usage_key = modulestore().make_course_usage_key(self.course_key)
        # the following two retrieve the same object
        self.course = get_course_by_id(course_key=self.course_key)
        self.course_module = modulestore().get_course(
            as_course_key(self.course_key), depth=self.depth)
        self.course_structure = cs_api.course_structure(self.course_key)
        self.course_outline_root_block = self.get_block_tree()

    def get_sequences(self):
        return modulestore().get_items(
            self.course_key, qualifiers={'category': 'sequential'})

    def get_blocks(self):
        '''
        >>> blocks.keys()
        ['root', 'blocks']
        blocks['root'] is a unicode string for the course block id
        u'block-v1:edX+DemoX+Demo_Course+type@course+block@course'
        '''
        all_blocks = get_blocks(
            request=None,
            usage_key=self.course_usage_key,
            user=None,
            nav_depth=3,
            requested_fields=['children', 'display_name', 'type', 'due', 'graded', 'special_exam_info', 'format'],
            block_types_filter=['course', 'chapter', 'sequential']
            )

        return all_blocks

    def get_block_tree(self):
        return get_course_outline_block_tree(
            make_fake_http_request(),
            str(self.course_key))

    def inspect(self):
        for rec in self.course_module.get_children():
            print(rec)


def test():
    course_key = as_course_key('course-v1:edX+DemoX+Demo_Course')
    cs = CourseStructure(course_key)

    return cs
