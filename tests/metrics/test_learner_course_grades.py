'''Test the figures.metrics.LearnerCourseGrades class

'''

from __future__ import absolute_import
from collections import OrderedDict
import datetime

from django.utils.timezone import utc
import mock
import pytest

from figures.metrics import LearnerCourseGrades

from tests.factories import (
    CourseEnrollmentFactory,
    GeneratedCertificateFactory,
    )

from tests.helpers import OPENEDX_RELEASE, GINKGO

# Mock objects to test course and course section grade metrics
if OPENEDX_RELEASE == GINKGO:
    from lms.djangoapps.grades.new.course_grade import (
        MockAggregatedScore,
        MockSubsectionGrade,
        )

else:
    from lms.djangoapps.grades.course_grade import (
        MockAggregatedScore,
        MockSubsectionGrade,
        )


@pytest.mark.django_db
class TestLearnerCourseGrades(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.course_enrollment = CourseEnrollmentFactory()
        if OPENEDX_RELEASE == GINKGO:
            self.course_id = self.course_enrollment.course_id
        else:
            self.course_id = self.course_enrollment.course.id

        self.lcg = LearnerCourseGrades(self.course_enrollment.user.id,
                                       self.course_id)

        # set up our sections
        # This is a quick job. We can do it cleaner
        # We do want to label each subsection grade
        # to make it easier to identify them in the 
        # tests
        
        self.msg1 = MockSubsectionGrade(tw_earned=0.0,tw_possible=0.0),
        self.msg2 = MockSubsectionGrade(tw_earned=0.0,tw_possible=0.5)
        self.msg3 = MockSubsectionGrade(tw_earned=0.5,tw_possible=1.0)

        self.graded_sections = [self.msg2, self.msg3]
        self.all_sections = [self.msg1, self.msg2, self.msg3]

        self.lcg.course_grade.chapter_grades = OrderedDict(
                alpha=dict(
                    sections=[self.msg1],
                    url_name=u'ec7e84694fca2d073731a462a5916a7a',
                    display_name=u'Module 1 - Overview',
                ),
                bravo=dict(
                    sections=[self.msg2, self.msg3],
                    url_name=u'2f43c0b7da59ed40156155f9a8ca4d40',
                    display_name=u'Module 2 - First Principles',
                    )
            )

    def test_str_rep(self):
        '''Test the string representation, __str__
        '''
        assert self.lcg.__str__()

    def test_chapter_grades(self):
        '''Tests the 'chapter_grades' property

        Because course grades are mocked, we are not interested in inspecting
        the contents of 'chapter_grades'

        This test was written when the chapter_grades were defined in the mocks.
        Since then we define them here to better control the values/structure
        for these tests and provide immediate (Same source file) context for
        the data used in these tests
        '''
        assert isinstance(self.lcg.chapter_grades, dict)
        # get the sub-dict of the first key
        keys = list(self.lcg.chapter_grades.keys())
        assert set(self.lcg.chapter_grades[keys[0]].keys()) == set([
            'sections', 'url_name', 'display_name'])

    def test_certificate_and_completion(self):
        '''
        We're testing both certificate completion because currently, the only
        way to tell if a user
        '''
        # We shouldn't have any certificates for this
        # course enrollment
        assert not self.lcg.certificates()
        assert not self.lcg.learner_completed()
        # Create a certificate record for this user
        expected_cert = GeneratedCertificateFactory(
            user=self.lcg.learner,
            course_id=self.lcg.course.id,
            created_date=datetime.datetime(2018, 6, 1, tzinfo=utc))
        assert expected_cert
        check_certs = self.lcg.certificates()
        assert check_certs.count() == 1
        assert check_certs[0] == expected_cert
        assert self.lcg.learner_completed()


    @pytest.mark.parametrize('tw_earned, tw_possible, check', [
            (0.0, 0.0, False),
            (0.0, 0.5, True),
            (0.5, 1.0, True),
        ])
    def test_is_section_graded(self, tw_earned, tw_possible, check):
        '''Validates the check if a section is graded

        Method does not rely on class instance values

        '''
        section = MockSubsectionGrade(
            tw_earned=tw_earned, tw_possible=tw_possible)
        assert self.lcg.is_section_graded(section) == check

    #
    # The following two tests test retrieving sections from chapter grades
    #
    # We have two methods instead of parametrizing for simplicity and that
    # decorators can't accept class instance variables for the class method
    # for which the decorator is applied. We would have to build our test
    # data outside of the class

    def test_sections_all(self):
        '''
        LearnerCourseGrade.sections_list uses the 'sections' iterator method so
        we can test both with the 'sections_list' method
        '''

        sections = self.lcg.sections_list()
        assert set(sections) == set(self.all_sections)
        sections = self.lcg.sections_list(only_graded=False)
        assert set(sections) == set(self.all_sections)

    def test_sections_graded(self):
        sections = self.lcg.sections_list(only_graded=True)
        assert set(sections) == set(self.graded_sections)

    def test_progress(self):
        progress = self.lcg.progress()
        expected = dict(
            count=len(self.graded_sections),
            points_possible=sum(rec.all_total.possible
                for rec in self.graded_sections),
            points_earned=sum(rec.all_total.earned
                for rec in self.graded_sections),
            sections_worked=len([rec for rec in self.graded_sections
                if rec.all_total.earned > 0])
        )
        assert progress == expected

        expected_progress_percent = float(
            expected['sections_worked'])/float(expected['count'])
        assert self.lcg.progress_percent() == expected_progress_percent

        assert self.lcg.progress_percent(expected) == expected_progress_percent

    def test_progress_percent_no_count(self):
        '''
        This test makes sure that we don't get a divide by zero error in the
        progress percent
        '''
        progress_details = dict(
            count=0,
            points_possible=0.0,
            points_earned=0.0,
            sections_worked=0,
        )

        assert self.lcg.progress_percent(progress_details) == 0.0


#
# Test LearnerCourseGrades static methods
#


@pytest.mark.django_db
def test_lcg_course_progress():
    '''
    This is a basic test. We want to expand on it to create specific mock values
    returned by CourseGradeFactory (assigned to LearnerCourseGrades
    course_grade.chapter_grades attributes)

    The expected data are pulled from the hardcoded values in the mocks.
    See ``tests/mocks/lms/djangoapps/grades/course_grade.py``
    '''
    expected = dict(
        progress_percent=0.5,
        course_progress_details=dict(
            count=2,
            sections_worked=1,
            points_possible=1.5,
            points_earned=0.5,
            ))
    course_enrollment = CourseEnrollmentFactory()
    course_progress = LearnerCourseGrades.course_progress(course_enrollment)
    assert course_progress == expected
