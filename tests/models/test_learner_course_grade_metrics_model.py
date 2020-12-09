"""Tests Figures GradesCache model
"""
from __future__ import absolute_import
import datetime
import pytest

from django.contrib.sites.models import Site
from django.db.models.query import QuerySet
from figures.helpers import as_date
from figures.models import LearnerCourseGradeMetrics

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    LearnerCourseGradeMetricsFactory,
    SiteFactory,
    UserFactory,
    COURSE_ID_STR_TEMPLATE
)
from six.moves import range


def create_sample_completed_lcgm(site, user_count, course_count):
    """Generate test data

    TODO: Make this a parametrized fixture
    https://docs.pytest.org/en/3.1.3/example/parametrize.html

    We don't create CourseEnrollment objects because we don't need them as
    Figures models try to rely on the content and context of the data in the
    LMS and not the LMS models specifically
    """
    users = [UserFactory() for i in range(user_count)]
    # We need just the course_ids
    course_ids = [COURSE_ID_STR_TEMPLATE.format(i) for i in range(course_count)]

    # Two records for each enrollment, one shows not complete, one shows complete
    lcgm_data = [
        dict(
            date_for='2020-04-01',
            points_possible=40,
            points_earned=40,
            sections_possible=5,
            sections_worked=4),
        dict(
            date_for='2020-05-05',
            points_possible=50,
            points_earned=50,
            sections_possible=5,
            sections_worked=5)
    ]
    lcgm_list = []
    for user in users:
        for course_id in course_ids:
            for lcgm in lcgm_data:
                lcgm_list.append(LearnerCourseGradeMetricsFactory(
                    site=site,
                    user=user,
                    course_id=course_id,
                    date_for=lcgm['date_for'],
                    points_possible=lcgm['points_possible'],
                    points_earned=lcgm['points_earned'],
                    sections_possible=lcgm['sections_possible'],
                    sections_worked=lcgm['sections_worked']
                    )
                )
    return dict(
        lcgm_list=lcgm_list,
        users=users,
        course_ids=course_ids,
        site=site,
    )


@pytest.mark.django_db
def test_latest_lcgm_with_data(db):
    """Make sure the query works with a couple of existing models

    We create two LearnerCourseGradeMetrics models and test that the function
    retrieves the newer one
    """
    user = UserFactory()
    first_date = as_date('2020-02-02')
    second_date = as_date('2020-04-01')
    course_overview = CourseOverviewFactory()
    older_lcgm = LearnerCourseGradeMetricsFactory(user=user,
                                                  course_id=str(course_overview.id),
                                                  date_for=first_date)
    newer_lcgm = LearnerCourseGradeMetricsFactory(user=user,
                                                  course_id=str(course_overview.id),
                                                  date_for=second_date)
    assert older_lcgm.date_for != newer_lcgm.date_for
    obj = LearnerCourseGradeMetrics.objects.latest_lcgm(
        user=user, course_id=course_overview.id)
    assert obj == newer_lcgm


@pytest.mark.django_db
def test_latest_lcgm_with_empty_table(db):
    """Make sure the query works when there are no models to find

    Tests that the function returns None and does not fail when it cannot find
    any LearnerCourseGradeMetrics model instances
    """
    assert not LearnerCourseGradeMetrics.objects.count()
    user = UserFactory()
    course_overview = CourseOverviewFactory()
    obj = LearnerCourseGradeMetrics.objects.latest_lcgm(
        user=user, course_id=course_overview.id)
    assert not obj


@pytest.mark.django_db
class TestLearnerCourseGradeMetricsManager(object):
    """Test the Manager methods

    This is a quick hack job to get test coverage and make sure filtering works
    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = SiteFactory()

    def test_completed_ids_for_site_empty(self):
        """Make sure the method doesn't break if there are no LCGM records
        """
        data = LearnerCourseGradeMetrics.objects.completed_ids_for_site(self.site)
        assert isinstance(data, QuerySet)
        assert not data

    def test_completed_ids_for_site(self):
        """
        Example data
        ```
        {'course_id': u'course-v1:StarFleetAcademy+SFA2+2161', 'user_id': 1}
        ```
        """
        lcgm_data = create_sample_completed_lcgm(self.site,
                                                 user_count=2,
                                                 course_count=2)

        # Build lcgm w/out completion
        LearnerCourseGradeMetrics(site=self.site,
                                  sections_possible=2,
                                  sections_worked=1)
        data = LearnerCourseGradeMetrics.objects.completed_ids_for_site(self.site)
        # Check we have our expected data

        expected = [(a.id, b) for a in lcgm_data['users']
                    for b in lcgm_data['course_ids']]
        results = [(rec['user_id'], rec['course_id']) for rec in data]
        assert set(results) == set(expected)

    def test_completed_ids_for_user_list(self):
        """Test when we filter on a list of user ids
        """
        lcgm_data = create_sample_completed_lcgm(self.site,
                                                 user_count=4,
                                                 course_count=2)
        user_ids = [lcgm_data['users'][i].id for i in [0, 2]]
        data = LearnerCourseGradeMetrics.objects.completed_ids_for_site(self.site,
                                                                        user_ids=user_ids)
        expected = [(a.id, b) for a in lcgm_data['users']
                    for b in lcgm_data['course_ids'] if a.id in user_ids]
        results = [(rec['user_id'], rec['course_id']) for rec in data]
        assert set(results) == set(expected)

    def test_completed_ids_for_course_list(self):
        """Test when we filter on a set of course_ids
        """
        lcgm_data = create_sample_completed_lcgm(self.site,
                                                 user_count=2,
                                                 course_count=4)
        course_ids = [lcgm_data['course_ids'][i] for i in [0, 2]]
        data = LearnerCourseGradeMetrics.objects.completed_ids_for_site(self.site,
                                                                        course_ids=course_ids)
        expected = [(a.id, b) for a in lcgm_data['users']
                    for b in lcgm_data['course_ids'] if b in course_ids]
        results = [(rec['user_id'], rec['course_id']) for rec in data]
        assert set(results) == set(expected)

    def test_completed_ids_for_user_and_course_lists(self):
        """Test when we filter on a set of course_ids
        """
        lcgm_data = create_sample_completed_lcgm(self.site,
                                                 user_count=4,
                                                 course_count=4)
        user_ids = [lcgm_data['users'][i].id for i in [0, 2]]
        course_ids = [lcgm_data['course_ids'][i] for i in [0, 2]]
        data = LearnerCourseGradeMetrics.objects.completed_ids_for_site(self.site,
                                                                        user_ids=user_ids,
                                                                        course_ids=course_ids)
        expected = [(a.id, b) for a in lcgm_data['users']
                    for b in lcgm_data['course_ids'] if b in course_ids and a.id in user_ids]
        results = [(rec['user_id'], rec['course_id']) for rec in data]
        assert set(results) == set(expected)


@pytest.mark.django_db
class TestLearnerCourseGradeMetrics(object):
    """Unit tests for figures.models.LearnerCourseGradeMetrics model

    Initially performing basic sanity checks for code coverage

    """
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = Site.objects.first()
        self.date_for = datetime.date(2018, 2, 2)
        self.course_enrollment = CourseEnrollmentFactory()
        self.grade_data = dict(
            points_possible=10.0,
            points_earned=5.0,
            sections_worked=2,
            sections_possible=2
            )
        self.create_rec = self.grade_data.copy()
        self.create_rec.update(dict(
            site=self.site,
            date_for=self.date_for,
            user=self.course_enrollment.user,
            course_id=self.course_enrollment.course_id))

    def test_create(self):
        obj = LearnerCourseGradeMetrics(**self.create_rec)
        assert str(obj) == '{} {} {} {}'.format(
            None,
            self.create_rec['date_for'],
            self.create_rec['user'].username,
            self.create_rec['course_id'])

    def test_latest_lcgm_one_rec(self):
        rec = LearnerCourseGradeMetrics.objects.create(**self.create_rec)
        assert LearnerCourseGradeMetrics.objects.count() == 1
        obj = LearnerCourseGradeMetrics.objects.latest_lcgm(
            user=self.course_enrollment.user,
            course_id=str(self.course_enrollment.course_id))
        assert rec == obj

    def test_latest_lcgm_multiple_dates(self):
        assert LearnerCourseGradeMetrics.objects.count() == 0
        for date in [datetime.date(2018, 2, day) for day in range(1, 4)]:
            rec = self.create_rec.copy()
            last_day = date
            rec['date_for'] = date
            LearnerCourseGradeMetrics.objects.create(**rec)

        obj = LearnerCourseGradeMetrics.objects.latest_lcgm(
            user=self.course_enrollment.user,
            course_id=str(self.course_enrollment.course_id))
        assert last_day
        assert obj.date_for == last_day

    def test_progress_percent(self):
        expected = (self.grade_data['sections_worked'] /
                    self.grade_data['sections_possible'])
        obj = LearnerCourseGradeMetrics(**self.create_rec)
        assert obj.progress_percent == expected

    def test_progress_percent_zero_sections_possible(self):
        create_rec = self.create_rec.copy()
        create_rec['sections_possible'] = 0
        obj = LearnerCourseGradeMetrics(**create_rec)
        assert obj.progress_percent == 0.0

    def test_progress_details(self):
        obj = LearnerCourseGradeMetrics(**self.create_rec)
        assert obj.progress_details == self.grade_data
