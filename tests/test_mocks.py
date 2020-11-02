"""
This module tests the mocks and test factories
"""

from __future__ import absolute_import
import pytest

from tests.factories import (
    CohortMembershipFactory,
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    CourseUserGroupFactory,
    GeneratedCertificateFactory,
    StudentModuleFactory,
    )


@pytest.mark.django_db
class TestCourseEnrollment(object):
    def test_create_default_factory(self):
        obj = CourseEnrollmentFactory()
        assert obj


@pytest.mark.django_db
class TestCourseOverview(object):
    def test_create_default_factory(self):
        obj = CourseOverviewFactory()
        assert obj


@pytest.mark.django_db
class TestGeneratedCertificate(object):
    def test_create_default_factory(self):
        obj = GeneratedCertificateFactory()
        assert obj


@pytest.mark.django_db
class TestStudentModule(object):
    def test_create_student_module_factory(self):
        obj = StudentModuleFactory()
        assert obj


@pytest.mark.django_db
class TestCourseUserGroup(object):
    def test_create_course_user_group_factory(self):
        obj = CourseUserGroupFactory()
        assert obj


@pytest.mark.django_db
class TestCohortMembership(object):
    def test_create_cohort_membership_factory(self):
        obj = CohortMembershipFactory()
        assert obj

# TODO: Add test for UserProfile
