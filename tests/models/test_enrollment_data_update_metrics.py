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

from mock import patch

from django.contrib.sites.models import Site

from figures.helpers import (
    as_datetime, days_from, utc_yesterday
)
from figures.models import EnrollmentData, LearnerCourseGradeMetrics

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    EnrollmentDataFactory,
    LearnerCourseGradeMetricsFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
    StudentModuleFactory)
from tests.helpers import (
    organizations_support_sites
)

if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory

    def map_users_to_org(org, users):
        """Convenience method to simplify test code
        """
        [UserOrganizationMappingFactory(user=user,
                                        organization=org) for user in users]


# @pytest.mark.skipif(OPENEDX_RELEASE == GINKGO, reason='Breaks on CourseEnrollmentFactory')
@pytest.mark.django_db
class TestUpdateMetrics(object):
    """Test EnrollmentDataManager.update_metrics method

    """
    @pytest.fixture(autouse=True)
    def setup(self, db, settings):

        # Set up data that's the same for standalone or multisite
        self.date_for = utc_yesterday()
        self.site = Site.objects.first()
        self.courses = [CourseOverviewFactory(), CourseOverviewFactory()]

        # Two for "our" course, one for another course in the same site
        self.enrollments = [
            CourseEnrollmentFactory(course_id=self.courses[0].id),
            CourseEnrollmentFactory(course_id=self.courses[0].id),
            CourseEnrollmentFactory(course_id=self.courses[1].id),
        ]

        self.ce0_sm = StudentModuleFactory.from_course_enrollment(
            self.enrollments[0],
            created=as_datetime(self.date_for),
            modified=as_datetime(self.date_for))

        # Handle site mode specifices
        if organizations_support_sites():
            settings.FEATURES['FIGURES_IS_MULTISITE'] = True
            self.org = OrganizationFactory(sites=[self.site])
            for course in self.courses:
                OrganizationCourseFactory(organization=self.org,
                                          course_id=str(course.id))
            map_users_to_org(self.org, [ce.user for ce in self.enrollments])

            # For our tests, we focus on a single enrollment. We should not
            # need to stand up other site data, but if we find we do need to,
            # then here's the place to do it
        else:
            self.org = OrganizationFactory()

    def setup_data_for_force_checks(self):
        pass

    def test_new_records_yesterday(self):
        """Test new enrollment with first activity in the course yesterday
        """
        ce = self.enrollments[0]
        the_enrollment = {
            'site': self.site,
            'user': self.enrollments[0].user,
            'course_id': str(self.enrollments[0].course_id)
        }
        assert not EnrollmentData.objects.filter(**the_enrollment)

        ed, created = EnrollmentData.objects.update_metrics(self.site, ce)

        check_ed = EnrollmentData.objects.get(**the_enrollment)
        lcgm = LearnerCourseGradeMetrics.objects.latest_lcgm(ce.user, ce.course_id)
        assert check_ed == ed
        assert created
        assert check_ed.date_for == self.date_for
        assert lcgm.date_for == self.date_for

    def test_edrec_exists_older_lcgm(self):
        ce = self.enrollments[0]
        older_date = days_from(self.date_for, -2)

        # Create existing Figures records
        EnrollmentDataFactory(site=self.site,
                              user=ce.user,
                              course_id=str(ce.course_id),
                              date_for=older_date)
        older_lcgm = LearnerCourseGradeMetricsFactory(site=self.site,
                                                      user=ce.user,
                                                      course_id=str(ce.course_id),
                                                      date_for=older_date)

        # Make sure that the LCGM we created is the most recent one
        assert LearnerCourseGradeMetrics.objects.latest_lcgm(ce.user,
                                                             ce.course_id) == older_lcgm
        # assert lcgm1 == older_lcgm
        # run our code under test
        ed, created = EnrollmentData.objects.update_metrics(self.site, ce)
        # verify our Figures records are updated
        after_lcgm = LearnerCourseGradeMetrics.objects.latest_lcgm(ce.user, ce.course_id)
        after_ed = EnrollmentData.objects.get(site=self.site,
                                              user=ce.user,
                                              course_id=str(ce.course_id))
        assert after_lcgm.date_for == self.date_for
        assert after_ed.date_for == self.date_for

    def test_exists_no_force(self):
        ce = self.enrollments[0]
        construct_kwargs = dict(
            site=self.site,
            user=ce.user,
            course_id=str(ce.course_id),
            date_for=self.date_for)
        before_ed = EnrollmentDataFactory(**construct_kwargs)
        LearnerCourseGradeMetricsFactory(**construct_kwargs)
        with patch('figures.models.EnrollmentProgress._get_progress') as get_prog:
            ed, created = EnrollmentData.objects.update_metrics(self.site, ce)
            assert not get_prog.called
            assert ed == before_ed

    def test_force_update(self):
        ce = self.enrollments[0]

        # Create existing Figures records
        # We only need to assign one progress value but we assign the possible
        # and earned for one to make sure that the earned is not more than the
        # possible. We arbitrarily choose points. We could have also chosen
        # sections or assigned both
        construct_kwargs = dict(
            site=self.site,
            user=ce.user,
            course_id=str(ce.course_id),
            date_for=self.date_for,
            points_earned=5,
            points_possible=10)
        EnrollmentDataFactory(**construct_kwargs)
        before_lcgm = LearnerCourseGradeMetricsFactory(**construct_kwargs)

        fake_progress = dict(points_possible=50,
                             points_earned=25,
                             sections_possible=10,
                             sections_worked=5)

        with patch('figures.models.EnrollmentProgress._get_progress', return_value=fake_progress):
            ed, created = EnrollmentData.objects.update_metrics(self.site, ce, force_update=True)

        # verify our Figures records are updated
        lcgm = LearnerCourseGradeMetrics.objects.latest_lcgm(ce.user, ce.course_id)
        check_ed = EnrollmentData.objects.get(site=self.site,
                                              user=ce.user,
                                              course_id=str(ce.course_id))
        assert check_ed == ed
        assert not created
        assert check_ed.date_for == self.date_for
        assert check_ed.points_earned == fake_progress['points_earned']
        assert lcgm.date_for == self.date_for
        assert lcgm.id == before_lcgm.id
        # We only need to check one of the progress fields to know it was updated
        assert lcgm.points_earned == fake_progress['points_earned']
        # import pdb; pdb.set_trace()
