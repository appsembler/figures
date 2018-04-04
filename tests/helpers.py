'''
Helper methods for edx-figures testing
'''

def make_course_key_str(org, number, run='test-run'):
    '''

    '''
    return 'course-v1:{}+{}+{}'.format(
        org, number, run)
