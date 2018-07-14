'''

./common/lib/xmodule/xmodule/modulestore/django.py
'''

from contextlib import contextmanager


class MockCourse(object):
    note = 'I am a mock course object.'


class MockMixedModulestore(object):

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

    def get_course(course_id, depth):
        return MockCourse()

def modulestore():
    '''
    Need to mock:
    
        with modulestore().bulk_operations(course_key):
            course = modulestore().get_course(course_key, depth=depth)
    '''
    return MockMixedModulestore()

