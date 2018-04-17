'''
Helper methods for edx-figures testing
'''

def make_course_key_str(org, number, run='test-run', **kwargs):
    '''
    Helper method to create a string representation of a CourseKey
    '''
    return 'course-v1:{}+{}+{}'.format(org, number, run)

def is_close(a, b, rel_tol=1e-9, abs_tol=0.0):
    '''Tests relative closeness for floating point values
    See: https://www.python.org/dev/peps/pep-0485/#proposed-implementation
    '''
    return abs(a-b) <= max( rel_tol * max(abs(a), abs(b)), abs_tol )
