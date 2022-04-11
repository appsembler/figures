"""Tests figures.enrollment module
"""
from __future__ import absolute_import
from datetime import timedelta

import pytest
from faker import Faker

from figures.enrollment import (
    student_modules_for_enrollment,
    student_modules_for_enrollment_after_date,
    is_enrollment_data_out_of_date
)
from figures.helpers import as_date, as_datetime

from tests.factories import (
    CourseEnrollmentFactory,
    EnrollmentDataFactory,
    StudentModuleFactory,
)


fake = Faker()


@pytest.mark.django_db
class TestStudentModulesForEnrollmentAfterDate(object):
    """Tests figures.enrollment.student_modules_for_enrollment_after_date
    This test also exercises `student_modules_for_enrollment` function.
    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.enrollment = CourseEnrollmentFactory()

    def test_no_student_modules(self):
        qs = student_modules_for_enrollment_after_date(self.enrollment, fake.date())
        assert not qs.exists()

    def test_none_after(self):
        sm_date = fake.date_this_year()
        td_params = dict(days=1)
        check_date = sm_date + timedelta(**td_params)
        sm = StudentModuleFactory.from_course_enrollment(self.enrollment,
            modified=as_datetime(sm_date))
        qs = student_modules_for_enrollment_after_date(self.enrollment, check_date)
        assert not qs.exists()




@pytest.mark.django_db
class TestIsEnrollmentDataOutOfDate(object):
    """Tests figures.enrollment.is_enrollment_data_out_of_date
    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.enrollment = CourseEnrollmentFactory()

    def test_no_edrec_no_sm(self):
        assert is_enrollment_data_out_of_date(self.enrollment) == False

    def test_no_edrec_has_sm(self):
        StudentModuleFactory.from_course_enrollment(self.enrollment)
        assert is_enrollment_data_out_of_date(self.enrollment) == True

    def test_has_edrec_but_out_of_date(self):
        edrec = EnrollmentDataFactory.from_course_enrollment(
            self.enrollment, date_for=fake.date_this_year())

        sm_date_for = edrec.date_for + timedelta(days=1)
        StudentModuleFactory.from_course_enrollment(
            self.enrollment, modified=sm_date_for)
        assert is_enrollment_data_out_of_date(self.enrollment) == True

    def test_has_edrec_and_up_to_date(self):
        edrec = EnrollmentDataFactory.from_course_enrollment(self.enrollment)
        assert is_enrollment_data_out_of_date(self.enrollment) == False
