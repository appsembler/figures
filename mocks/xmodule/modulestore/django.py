'''

./common/lib/xmodule/xmodule/modulestore/django.py
'''

from __future__ import absolute_import
from contextlib import contextmanager


class MockCourse(object):
    '''
    This is a mock of the CourseDescriptor

    This usually seems to be a 'xblock.internal.CourseDescriptorWithMixins'
    object. Which appears to be an ephemeral class (yeah, let that sink in).
    which makes working with it a real joy since it also appears to not be
    documented anywhere, even though it might be one of the most important
    classes in Open edX.

    There is a 'CourseDescriptor' class in
        ``common/lib/xmodule/xmodule/course_module.py``

    So this mock is a minimal attempt
    '''
    note = 'I am a mock course object.'

    def __init__(self, course_locator, **kwargs):
        self.grading_policy = None
        self.id = course_locator
    def set_grading_policy(self, grading_policy):
        self.grading_policy = grading_policy


class MockMixedModulestore(object):
    '''
    We are mocking functionality needed by courseware.courses
    '''
    def __init__(self, **kwargs):
        pass

    @contextmanager
    def bulk_operations(self, course_id, emit_signals=True, ignore_Case=False):
        '''
        see xmodule/modulestore/__init__.py

        Bulk operations look like a likely candidate to extract from edx-platform

        For now, we're doing the absolute minimum mocking
        '''
        yield

    def get_course(self, course_id, depth):
        return MockCourse(course_locator=course_id)

def modulestore():
    '''
    Need to mock:
    
        with modulestore().bulk_operations(course_key):
            course = modulestore().get_course(course_key, depth=depth)
    '''

    # This is the production code:
    # We are skipping mocking the CCX modulestore
    # _MIXED_MODULESTORE = create_modulestore_instance(
    #     settings.MODULESTORE['default']['ENGINE'],
    #     contentstore(),
    #     settings.MODULESTORE['default'].get('DOC_STORE_CONFIG', {}),
    #     settings.MODULESTORE['default'].get('OPTIONS', {})
    # )

    return MockMixedModulestore()
