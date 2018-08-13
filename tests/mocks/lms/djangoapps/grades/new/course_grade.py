'''

'''
from collections import OrderedDict


class MockAggregatedScore(object):
    '''

    '''
    def __init__(self, tw_earned, tw_possible, **kwargs):
        self.graded = False
        self.first_attempted = None
        self.earned = float(tw_earned) if tw_earned is not None else None
        self.possible = float(tw_possible) if tw_possible is not None else None


class MockSubsectionGrade(object):
    '''

    '''
    def __init__(self, ):
        self.problem_scores = OrderedDict()
        self.all_total = MockAggregatedScore(tw_earned=0.0, tw_possible=0.0)


class CourseGrade(object):
    '''
    Production class inherits from CourseGradeBase
    '''
    def __init__(self, user, course_data, percent=0, letter_grade=None, passed=False, *args, **kwargs):
        self.user = user
        self.course_data = course_data,
        self.percent = percent
        self.passed = passed

    @property
    def chapter_grades(self):
        '''
        Mock for course_grades.CourseGradeBase.chapter_grades
        (which uses the @lazy decorator)

        for chapter_grade in self.course_grade.chapter_grades.values():
            for section in chapter_grade['sections']:

        we don't need the BlockUsageLocator key for our initial testing
        So we're just going to use the phonetic alphabet

        Use the following to generate additional url names
            ``binascii.b2a_hex(os.urandom(16))``

        Chapter grade keys are 'sections', 'url_name', and 'display_name'
        '''

        return OrderedDict(
            alpha=dict(
                sections=[
                    MockSubsectionGrade(),
                    MockSubsectionGrade(),
                    MockSubsectionGrade(),
                ],
                url_name=u'ec7e84694fca2d073731a462a5916a7a',
                display_name=u'Module 1 - Overview',
            ),
            bravo=dict(
                sections=[
                    MockSubsectionGrade(),
                    MockSubsectionGrade(),
                    MockSubsectionGrade(),
                ],
                url_name=u'2f43c0b7da59ed40156155f9a8ca4d40',
                display_name=u'Module 2 - First Principles',
            ),
        )
