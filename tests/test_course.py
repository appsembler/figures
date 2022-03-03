"""Test `figures.course` module

"""
from __future__ import absolute_import
import pytest
from faker import Faker
from opaque_keys.edx.keys import CourseKey

from figures.course import Course
from figures.helpers import days_from
from figures.sites import get_site_for_course

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    StudentModuleFactory,
)

fake = Faker()


@pytest.mark.django_db
class TestCourse:
    """
    Starting with just basic tests
    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.course_overview = CourseOverviewFactory()
        # Little sanity check making sure our Factory has the right class type
        # for the course key
        assert isinstance(self.course_overview.id, CourseKey)

    def assert_construction(self, course):
        assert course.course_key == self.course_overview.id
        assert course.course_id == str(self.course_overview.id)
        assert course.site == get_site_for_course(self.course_overview.id)

    def simple_test_property_course_id_association(self, factory_class, property_name):
        """Helper method to DRY tests for property methods on simple associations

        This method can be used to test the Course class property methods return
        expected results for property methods that return objects that can be
        associated with  a course with just the course id. Initially implemented
        to test the enrollments and student modules property methods. Could also
        be used to test for other models like CourseAccessGroup, CourseAccessRole,
        Figures CourseDailyMetrics,
        EnrollmentData, or LearnerCourseGradeMetrics if we wanted to implement
        property methods for those

        If we did use this for models that use a string course id instead of a
        CourseKey, then we'll need to make sure the handled course id form is
        used. We could do this with a method parameter that either casts to the
        expected form or defines which one to use and we can explicitly cast in
        this method
        """
        our_objects = [factory_class(course_id=self.course_overview.id)
                       for _ in range(2)]
        other_object = factory_class()
        assert not other_object.course_id == self.course_overview.id
        course = Course(self.course_overview.id)
        assert set(our_objects) == set(getattr(course, property_name))

    def test_str_constructor(self):
        self.assert_construction(Course(str(self.course_overview.id)))

    def test_course_key_constructor(self):
        self.assert_construction(Course(self.course_overview.id))

    def test_enrollments(self):
        self.simple_test_property_course_id_association(CourseEnrollmentFactory,
                                                        'enrollments')

    def test_student_modules(self):
        self.simple_test_property_course_id_association(StudentModuleFactory,
                                                        'student_modules')

    def test_student_modules_active_on_date(self):
        our_date_for = fake.date_this_year()
        our_created_sm = [StudentModuleFactory(course_id=self.course_overview.id,
                                               created=our_date_for) for _ in range(2)]
        our_modified_sm = [StudentModuleFactory(course_id=self.course_overview.id,
                                                modified=our_date_for) for _ in range(2)]
        # Create record with a different date
        StudentModuleFactory(course_id=self.course_overview.id,
                             created=days_from(our_date_for, -2),
                             modified=days_from(our_date_for, -1))
        course = Course(self.course_overview.id)
        found_sm = course.student_modules_active_on_date(our_date_for)
        assert set(our_created_sm + our_modified_sm) == set(found_sm)

    def test_enrollments_active_on_date(self):
        our_date_for = fake.date_this_year()
        other_date_for = days_from(our_date_for, -1)
        our_ce = [CourseEnrollmentFactory(course_id=self.course_overview.id)
                  for _ in range(2)]
        our_sm = []
        for ce in our_ce:
            our_sm.extend([
                StudentModuleFactory.from_course_enrollment(ce, modified=our_date_for),
                StudentModuleFactory.from_course_enrollment(ce, created=our_date_for)
                ])
        # Create enrollment we should not get in our results
        other_ce = CourseEnrollmentFactory(course_id=self.course_overview.id)
        StudentModuleFactory.from_course_enrollment(other_ce,
                                                    created=other_date_for,
                                                    modified=other_date_for)
        course = Course(self.course_overview.id)
        found_ce = course.enrollments_active_on_date(our_date_for)
        assert set(found_ce) == set(our_ce)
