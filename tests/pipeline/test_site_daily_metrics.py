'''Tests figures.pipeline.site_daily_metrics module

IMPORTANT: We need to refactor the test data in this test module as this was
early work and we've learned a lot since then.

TODO:

* Add tests for the individual field extractors
* Add test coverage for multisite mode
'''

from __future__ import absolute_import
import datetime
import pytest

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils.timezone import utc

from figures.compat import StudentModule

from figures.helpers import as_datetime, prev_day, days_from, is_multisite
from figures.models import SiteDailyMetrics
from figures.pipeline import site_daily_metrics as pipeline_sdm
import figures.sites

from tests.factories import (
    CourseDailyMetricsFactory,
    CourseOverviewFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
    SiteDailyMetricsFactory,
    StudentModuleFactory,
    UserFactory,
)

from tests.helpers import organizations_support_sites
import six
from six.moves import range


if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory


DEFAULT_START_DATE = datetime.datetime(2018, 1, 1, 0, 0, tzinfo=utc)
DEFAULT_END_DATE = datetime.datetime(2018, 3, 1, 0, 0, tzinfo=utc)

# Course Daily Metrics data
CDM_INPUT_TEST_DATA = [
    dict(
        enrollment_count=0,
        active_learners_today=0,
        average_progress=None,
        average_days_to_complete=None,
        num_learners_completed=0),
    dict(
        enrollment_count=50,
        active_learners_today=5,
        average_progress=0.25,
        average_days_to_complete=24,
        num_learners_completed=0),
    dict(
        enrollment_count=100,
        active_learners_today=10,
        average_progress=0.75,
        average_days_to_complete=12,
        num_learners_completed=5),
]

# Previous day's SiteDailyMetrics data
SDM_DATA = [
    None,
    dict(
        cumulative_active_user_count=50,
        todays_active_user_count=10,
        total_user_count=200,
        course_count=len(CDM_INPUT_TEST_DATA),
        total_enrollment_count=100,
        mau=55,
    )
]

# Expected results for extracting data for SiteDailyMetrics
SDM_EXPECTED_RESULTS = dict(
    cumulative_active_user_count=65,
    todays_active_user_count=15,
    total_user_count=200,
    course_count=len(CDM_INPUT_TEST_DATA),
    total_enrollment_count=150,
    mau=56,
    )


@pytest.mark.django_db
class TestCourseDailyMetricsMissingCdm(object):
    '''
    TODO: Do we want to add a test for when there are no courses?
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.date_for = DEFAULT_END_DATE
        self.site = Site.objects.first()
        self.course_count = 4
        self.course_overviews = [CourseOverviewFactory(
            created=self.date_for) for i in range(self.course_count)]
        if is_multisite():
            self.organization = OrganizationFactory(sites=[self.site])
            for co in self.course_overviews:
                OrganizationCourseFactory(organization=self.organization,
                                          course_id=str(co.id))

    def test_no_missing(self):
        [CourseDailyMetricsFactory(
            date_for=self.date_for,
            site=self.site,
            course_id=course.id) for course in self.course_overviews]
        course_ids = pipeline_sdm.missing_course_daily_metrics(
            site=self.site,
            date_for=self.date_for)
        assert course_ids == set([])

    def test_missing(self):
        [
            CourseDailyMetricsFactory(
                date_for=self.date_for,
                site=self.site,
                course_id=self.course_overviews[0].id),
            CourseDailyMetricsFactory(
                date_for=self.date_for,
                site=self.site,
                course_id=self.course_overviews[1].id),
        ]
        expected_missing = [six.text_type(co.id) for co in self.course_overviews[2:]]
        actual = pipeline_sdm.missing_course_daily_metrics(
            site=self.site, date_for=self.date_for)

        assert set([str(obj) for obj in actual]) == set(expected_missing)


@pytest.mark.django_db
class TestSiteDailyMetricsPipelineFunctions(object):
    '''
    Run tests on standalone methods in pipeline.site_daily_metrics
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.date_for = datetime.date(2018, 6, 1)
        self.site = Site.objects.first()
        self.cdm_recs = [CourseDailyMetricsFactory(
            site=self.site,
            date_for=self.date_for,
            **cdm
            ) for cdm in CDM_INPUT_TEST_DATA]

    def test_get_active_user_count_for_date(self, monkeypatch):
        assert not get_user_model().objects.count()
        assert not StudentModule.objects.count()
        modified = as_datetime(self.date_for)

        def mock_student_modules_for_site(site):
            for user in [UserFactory() for i in range(2)]:
                StudentModuleFactory(student=user, modified=modified)
                StudentModuleFactory(student=user, modified=modified)
            return StudentModule.objects.all()

        monkeypatch.setattr(pipeline_sdm, 'get_student_modules_for_site',
                            mock_student_modules_for_site)
        users = pipeline_sdm.get_site_active_users_for_date(site=self.site,
                                                            date_for=self.date_for)
        assert users.count() == get_user_model().objects.count()

    @pytest.mark.parametrize('prev_day_data, expected', [
        (SDM_DATA[0], 0,),
        (SDM_DATA[1], SDM_DATA[1]['cumulative_active_user_count'],),
    ])
    def test_get_previous_cumulative_active_user_count(self, prev_day_data, expected):
        if prev_day_data:
            SiteDailyMetricsFactory(
                site=self.site,
                date_for=prev_day(self.date_for),
                **prev_day_data)
        actual = pipeline_sdm.get_previous_cumulative_active_user_count(
            site=self.site,
            date_for=self.date_for)
        assert actual == expected

    def test_get_previous_cumulative_active_user_count_not_yesterday(self):
        prior_date = days_from(self.date_for, -5)
        prior_sdm = SiteDailyMetricsFactory(site=self.site,
                                            date_for=prior_date,
                                            **SDM_DATA[1])
        actual = pipeline_sdm.get_previous_cumulative_active_user_count(
            site=self.site,
            date_for=self.date_for)
        assert prior_sdm.cumulative_active_user_count > 0
        assert actual == prior_sdm.cumulative_active_user_count

    def test_get_total_enrollment_count(self):
        expected = SDM_EXPECTED_RESULTS['total_enrollment_count']
        actual = pipeline_sdm.get_total_enrollment_count(
            site=self.site,
            date_for=self.date_for)
        assert actual == expected


@pytest.mark.django_db
class TestSiteDailyMetricsExtractor(object):
    '''
    TODO: We need to test with ``date_for`` as both for now and a time in the past
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.date_for = datetime.date(2018, 10, 1)
        self.site = Site.objects.first()
        self.users = [UserFactory(
            date_joined=as_datetime(self.date_for - datetime.timedelta(days=60))
            ) for i in range(0, 3)]
        self.course_overviews = [CourseOverviewFactory(
            created=as_datetime(self.date_for - datetime.timedelta(days=60))
            ) for i in range(0, 3)]
        self.cdm_recs = [CourseDailyMetricsFactory(
            site=self.site,
            date_for=self.date_for,
            **cdm
            ) for cdm in CDM_INPUT_TEST_DATA]
        self.prev_day_sdm = SiteDailyMetricsFactory(
            site=self.site,
            date_for=prev_day(self.date_for),
            **SDM_DATA[1])

        if is_multisite():
            self.organization = OrganizationFactory(sites=[self.site])
            for co in self.course_overviews:
                OrganizationCourseFactory(organization=self.organization,
                                          course_id=str(co.id))
            if organizations_support_sites():
                for user in self.users:
                    UserOrganizationMappingFactory(user=user,
                                                   organization=self.organization)

    def test_extract(self, monkeypatch):
        previous_cumulative_active_user_count = 50

        expected_results = dict(
            cumulative_active_user_count=52,  # previous cumulative is 50
            todays_active_user_count=2,
            total_user_count=len(self.users),
            course_count=len(CDM_INPUT_TEST_DATA),
            total_enrollment_count=150,
            mau=len(self.users),  # expect 3
        )

        assert not StudentModule.objects.count()
        modified = as_datetime(self.date_for)

        def mock_student_modules_for_site(site):
            users = [UserFactory() for i in range(2)]
            for user in users:
                StudentModuleFactory(student=user, modified=modified)
                StudentModuleFactory(student=user, modified=modified)
            return StudentModule.objects.filter(student__in=users)

        monkeypatch.setattr(pipeline_sdm, 'get_student_modules_for_site',
                            mock_student_modules_for_site)

        def mock_site_mau_1g_for_month_as_of_day(site, date_for):
            return get_user_model().objects.filter(
                id__in=[user.id for user in self.users]).values('id')

        monkeypatch.setattr(pipeline_sdm, 'site_mau_1g_for_month_as_of_day',
                            mock_site_mau_1g_for_month_as_of_day)

        def mock_get_previous_cumulative_active_user_count(site, date_for):
            return previous_cumulative_active_user_count

        monkeypatch.setattr(pipeline_sdm, 'get_previous_cumulative_active_user_count',
                            mock_get_previous_cumulative_active_user_count)

        for course in figures.sites.get_courses_for_site(self.site):
            assert course.created.date() < self.date_for
        for user in figures.sites.get_users_for_site(self.site):
            assert user.date_joined.date() < self.date_for

        actual = pipeline_sdm.SiteDailyMetricsExtractor().extract(
            site=self.site,
            date_for=self.date_for)

        for key, value in six.iteritems(expected_results):
            assert actual[key] == value, 'failed on key: "{}"'.format(key)


@pytest.mark.django_db
class TestSiteDailyMetricsLoader(object):
    """
    Tests the site metrics loading for single site (standalone) deployments

    """
    FIELD_VALUES = dict(
                todays_active_user_count=1,
                cumulative_active_user_count=2,
                total_user_count=3,
                course_count=4,
                total_enrollment_count=5,
                mau=6,
                )

    class MockExtractor(object):
        def extract(self, **kwargs):
            return TestSiteDailyMetricsLoader.FIELD_VALUES

    @pytest.fixture(autouse=True)
    def setup(self, db):
        pass

    def test_load_for_today(self):
        assert Site.objects.count() == 1
        assert SiteDailyMetrics.objects.count() == 0
        loader = pipeline_sdm.SiteDailyMetricsLoader(
            extractor=self.MockExtractor())
        site_metrics, created = loader.load(site=Site.objects.first())

        sdm = SiteDailyMetrics.objects.first()
        for key, value in six.iteritems(self.FIELD_VALUES):
            assert getattr(sdm, key) == value, 'failed on key: "{}"'.format(key)

    @pytest.mark.skip('Test stub')
    def test_no_course_overviews(self):
        pass
