'''

./common/lib/xmodule/xmodule/modulestore/django.py
'''

from contextlib import contextmanager


class MockCourse(object):
    note = 'I am a mock course object.'

    def __init__(self,**kwargs):
        self.grading_policy = None

    def set_grading_policy(self, grading_policy):
        self.grading_policy = grading_policy


class MockMixedModulestore(object):
    '''
    We are mocking functionalit needed by courseware.courses
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
        return MockCourse()

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
