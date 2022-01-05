'''

'''
from __future__ import absolute_import
from collections import OrderedDict


class MockAggregatedScore(object):
    '''

    '''
    def __init__(self, tw_earned, tw_possible, **kwargs):
        self.graded = False
        self.first_attempted = None
        self.earned = float(tw_earned) if tw_earned is not None else None
        self.possible = float(tw_possible) if tw_possible is not None else None

    def __str__(self):
        return 'earned={}, possible={}, graded={}, first_attempted={}'.format(
            self.earned, self.possible, self.graded, self.first_attempted)

    def __repr__(self):
        return self.__str__()


class MockSubsectionGrade(object):
    '''

    '''
    def __init__(self, **kwargs):
        self.problem_scores = OrderedDict()
        self.all_total = MockAggregatedScore(
            tw_earned=kwargs.get('tw_earned', 0.0),
            tw_possible=kwargs.get('tw_possible', 0.0)
        )

    def __str__(self):
        return 'all_total={}'.format(self.all_total)

    def __repr__(self):
        return self.__str__()

def create_chapter_grades():
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
                MockSubsectionGrade(tw_earned=0.0, tw_possible=0.0),
                MockSubsectionGrade(tw_earned=0.0,tw_possible=0.5),
                MockSubsectionGrade(tw_earned=0.5,tw_possible=1.0),
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


class CourseGrade(object):
    '''
    Production class inherits from CourseGradeBase
    '''
    def __init__(self, user, course_data, percent=0, letter_grade=None, passed=False, *args, **kwargs):
        self.user = user
        self.course_data = course_data,
        self.percent = percent
        self.passed = passed

        # Convert empty strings to None when reading from the table
        self.letter_grade = letter_grade or None
        self.chapter_grades = kwargs.get('chapter_grades',
            create_chapter_grades())

    @property
    def summary(self):
        """
        Returns the grade summary as calculated by the course's grader.
        DEPRECATED: To be removed as part of TNL-5291.
        """
        # TODO(TNL-5291) Remove usages of this deprecated property.
        # grade_summary = self.grader_result
        grade_summary = {}
        grade_summary['percent'] = self.percent
        grade_summary['grade'] = self.letter_grade
        return grade_summary
