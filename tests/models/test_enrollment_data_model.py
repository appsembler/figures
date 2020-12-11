"""
Basic tests for figures.models.EnrollmentData model

Test scenarios we need to help verify the data model

1. Learner doesn't have a CourseEnrollment (CE)
2. Learner just signed up. Has a CE, no LearnerCourseGradeMetric (LCGM)
3. Learner has CE and one LCGM
4. Learner has CE and multiple LCGM
5. Learner completed the course
6. Learner is no longer active in the course (Note: this is only handled in
   our data by the fact that the EnrollmentData.is_active field would be False)
7+ The test scenrios we haven't identified yet


Tests fail in Ginkgo due to
    "TypeError: 'course' is an invalid keyword argument for this function"

Which is interesting because other tests use CourseEnrollmentFactory(course=X)
and they do not fail in Ginkgo. For now, skipping test in Ginkgo
"""

import pytest

from figures.models import EnrollmentData

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    EnrollmentDataFactory,
    LearnerCourseGradeMetricsFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
    SiteFactory,
    UserFactory)
from tests.helpers import (
    OPENEDX_RELEASE,
    GINKGO,
    organizations_support_sites
)

if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory

    def map_users_to_org(org, users):
        [UserOrganizationMappingFactory(user=user,
                                        organization=org) for user in users]


@pytest.mark.django_db
def make_site_data(num_users=3, num_courses=2):
    """
    This is a copy-n-paste hack from figures/tests/conftest.py
    """
    site = SiteFactory()
    if organizations_support_sites():
        org = OrganizationFactory(sites=[site])
    else:
        org = OrganizationFactory()
    courses = [CourseOverviewFactory() for i in range(num_courses)]
    users = [UserFactory() for i in range(num_users)]
    enrollments = []

    users = [UserFactory() for i in range(num_users)]

    enrollments = []
    for i, user in enumerate(users):
        # Create increasing number of enrollments for each user, maximum to one less
        # than the number of courses
        for j in range(i):
            enrollments.append(
                CourseEnrollmentFactory(course=courses[j-1], user=user)
            )

    if organizations_support_sites():
        for course in courses:
            OrganizationCourseFactory(organization=org,
                                      course_id=str(course.id))

        # Set up user mappings
        map_users_to_org(org, users)

    return dict(
        site=site,
        org=org,
        courses=courses,
        users=users,
        enrollments=enrollments,
    )


@pytest.fixture
@pytest.mark.django_db
def site_data(db, settings):
    """Simple fake site data
    """
    if organizations_support_sites():
        settings.FEATURES['FIGURES_IS_MULTISITE'] = True
    site_data = make_site_data()

    ce = site_data['enrollments'][0]

    lcgm = [
        LearnerCourseGradeMetricsFactory(site=site_data['site'],
            user=ce.user,
            course_id=str(ce.course_id),
            date_for='2020-10-01'),
    ]

    site_data['lcgm'] = lcgm
    return site_data


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO, reason='Breaks on CourseEnrollmentFactory')
def test_set_enrollment_data_new_record(site_data):
    """Test we create a new EnrollmentData record

    Barebone test on creating a new EnrollmentData record for an existing
    LCGM record.
    """
    site = site_data['site']
    ce = site_data['enrollments'][0]
    lcgm = site_data['lcgm'][0]

    assert lcgm.course_id == str(ce.course_id)
    assert lcgm.user_id == ce.user_id
    assert not EnrollmentData.objects.count()
    obj, created = EnrollmentData.objects.set_enrollment_data(
        site=site,
        user=ce.user,
        course_id=ce.course_id)

    assert obj and created
    assert obj.user == lcgm.user


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO, reason='Breaks on CourseEnrollmentFactory')
def test_set_enrollment_data_update_existing(site_data):
    """Test we update an existing EnrollmentData record
    """
    site = site_data['site']
    ce = site_data['enrollments'][0]
    lcgm = site_data['lcgm'][0]
    ed = EnrollmentDataFactory(site=site,
                               course_id=str(ce.course_id),
                               user=ce.user)
    assert EnrollmentData.objects.count() == 1
    obj, created = EnrollmentData.objects.set_enrollment_data(
        site=site,
        user=ce.user,
        course_id=ce.course_id)
    assert EnrollmentData.objects.count() == 1
