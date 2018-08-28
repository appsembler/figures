'''
This module tests the mocks and test factories
'''

import pytest

from certificates.models import GeneratedCertificate

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    GeneratedCertificateFactory,
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


# TODO: Add test for UserProfile