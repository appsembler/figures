'''
This module tests the mocks and test factories
'''

import datetime
import pytest
import pytz

from certificates.models import GeneratedCertificate

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    GeneratedCertificateFactory,
    StudentModuleFactory,
    )


@pytest.mark.django_db
class TestCourseEnrollment(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        pass


    def test_create_default_factory(self):
        cert =  CourseEnrollmentFactory()


@pytest.mark.django_db
class TestCourseOverview(object):
    @pytest.fixture(autouse=True)
    def setup(self, db):
        pass

    def test_create_default_factory(self):
        course_overview = CourseOverviewFactory()


@pytest.mark.django_db
class TestGeneratedCertificate(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        pass

    def test_create_default_factory(self):
        cert =  GeneratedCertificateFactory()
        assert cert


@pytest.mark.django_db
class TestStudentModule(object):
    @pytest.fixture(autouse=True)
    def setup(self, db):
        pass

    def test_create_student_module_factory(self):
        obj = StudentModuleFactory()
        assert obj

# TODO: Add test for UserProfile
