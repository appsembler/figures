"""

"""

from __future__ import absolute_import
from datetime import date
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError

import pytest

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)

from figures.helpers import as_course_key, as_date
from figures.models import (
    CourseDailyMetrics,
    PipelineError,
    SiteDailyMetrics,
    )
import figures.tasks
import figures.mau

from tests.factories import (
    CourseDailyMetricsFactory,
    CourseMauMetricsFactory,
    CourseOverviewFactory,
    SiteFactory,
    SiteDailyMetricsFactory,
    SiteMonthlyMetricsFactory,
    )

from six.moves import range
from tests.helpers import OPENEDX_RELEASE, GINKGO


def test_populate_single_cdm(transactional_db, monkeypatch):
    assert CourseDailyMetrics.objects.count() == 0
    date_for = '2019-01-02'
    course_id = "course-v1:certs-appsembler+001+2019"
    created = False

    def mock_cdm_load(self, date_for, **kwargs):
        return (CourseDailyMetricsFactory(date_for=date_for), created, )

    monkeypatch.setattr(
        figures.pipeline.course_daily_metrics.CourseDailyMetricsLoader,
        'load', mock_cdm_load)
    figures.tasks.populate_single_cdm(course_id, date_for)

    assert CourseDailyMetrics.objects.count() == 1
    assert as_date(CourseDailyMetrics.objects.first().date_for) == as_date(date_for)


def test_populate_site_daily_metrics(transactional_db, monkeypatch):
    assert SiteDailyMetrics.objects.count() == 0
    date_for = '2019-01-02'
    created = False
    site = SiteFactory()

    def mock_sdm_load(self, site, date_for, **kwargs):
        return (SiteDailyMetricsFactory(site=site), created, )

    monkeypatch.setattr(
        figures.pipeline.site_daily_metrics.SiteDailyMetricsLoader,
        'load', mock_sdm_load)
    figures.tasks.populate_site_daily_metrics(site.id, date_for=date_for)

    assert SiteDailyMetrics.objects.count() == 1


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO,
                    reason='Broken test. Apparent Django 1.8 incompatibility')
def test_populate_daily_metrics_site_level_error(transactional_db,
                                                 monkeypatch,
                                                 caplog):
    date_for = '2019-01-02'
    error_message = dict(message=[u'expected failure'])
    assert not CourseOverview.objects.count()

    def mock_get_courses_fail(site):
        raise Exception(message=error_message)

    assert SiteDailyMetrics.objects.count() == 0
    assert CourseDailyMetrics.objects.count() == 0
    monkeypatch.setattr(
        figures.sites, 'get_courses_for_site', mock_get_courses_fail)

    figures.tasks.populate_daily_metrics(date_for=date_for)

    last_log = caplog.records[-1]
    assert last_log.message.startswith(
        'FIGURES:FAIL populate_daily_metrics unhandled site level exception for site')


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO,
                    reason='Broken test. Apparent Django 1.8 incompatibility')
def test_populate_daily_metrics_error(transactional_db, monkeypatch):
    date_for = '2019-01-02'
    error_message = dict(message=[u'expected failure'])
    assert not CourseOverview.objects.count()

    def mock_get_courses(site):
        CourseOverviewFactory()
        return CourseOverview.objects.all()

    def mock_pop_single_cdm_fails(**kwargs):
        # TODO: test with different exceptions
        # At least one with and without `message_dict`
        raise ValidationError(message=error_message)

    assert SiteDailyMetrics.objects.count() == 0
    assert CourseDailyMetrics.objects.count() == 0
    monkeypatch.setattr(
        figures.sites, 'get_courses_for_site', mock_get_courses)
    monkeypatch.setattr(
        figures.tasks, 'populate_single_cdm', mock_pop_single_cdm_fails)
    assert PipelineError.objects.count() == 0
    figures.tasks.populate_daily_metrics(date_for=date_for)
    assert PipelineError.objects.count() == 1
    error_data = PipelineError.objects.first().error_data
    assert error_data['message_dict']['message'] == error_message['message']


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO,
                    reason='Broken test. Apparent Django 1.8 incompatibility')
def test_populate_daily_metrics_enrollment_data_error(transactional_db,
                                                      monkeypatch,
                                                      caplog):
    date_for = '2019-01-02'
    error_message = dict(message=[u'expected failure'])
    assert not CourseOverview.objects.count()

    def mock_get_courses(site):
        CourseOverviewFactory()
        return CourseOverview.objects.all()

    def mock_pop_single_cdm(**kwargs):
        pass

    def mock_update_enrollment_data_fails(**kwargs):
        # TODO: test with different exceptions
        # At least one with and without `message_dict`
        raise Exception(message=error_message)

    assert SiteDailyMetrics.objects.count() == 0
    assert CourseDailyMetrics.objects.count() == 0
    monkeypatch.setattr(
        figures.sites, 'get_courses_for_site', mock_get_courses)
    monkeypatch.setattr(
        figures.tasks, 'populate_single_cdm', mock_pop_single_cdm)
    monkeypatch.setattr(
        figures.tasks, 'update_enrollment_data', mock_update_enrollment_data_fails)

    figures.tasks.populate_daily_metrics(date_for=date_for)
    last_log = caplog.records[-1]
    assert last_log.message.startswith(
        'FIGURES:FAIL figures.tasks update_enrollment_data')


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO,
                    reason='Broken test. Apparent Django 1.8 incompatibility')
def test_populate_daily_metrics_multisite(transactional_db, monkeypatch):
    # Stand up test data
    date_for = '2019-01-02'
    site_links = []
    for domain in ['alpha.domain', 'bravo.domain']:
        site_links.append(dict(
            site=SiteFactory(domain=domain),
            courses=[CourseOverviewFactory() for i in range(2)],
        ))

        figures.tasks.populate_daily_metrics(date_for=date_for)


def test_populate_course_mau(transactional_db, monkeypatch):
    expected_site = SiteFactory()
    course = CourseOverviewFactory()

    def mock_collect_course_mau(site, courselike, month_for=None, overwrite=False):
        assert site == expected_site
        assert courselike
        assert isinstance(month_for, date)
        return CourseMauMetricsFactory(), True

    monkeypatch.setattr('figures.tasks.collect_course_mau',
                        mock_collect_course_mau)

    figures.tasks.populate_course_mau(site_id=expected_site.id,
                                      course_id=str(course.id))
    # TODO: Create own test function
    figures.tasks.populate_course_mau(site_id=expected_site.id,
                                      course_id=str(course.id),
                                      month_for=None)
    figures.tasks.populate_course_mau(site_id=expected_site.id,
                                      course_id=str(course.id),
                                      month_for='2020-1-1')


def test_populate_mau_metrics_for_site(transactional_db, monkeypatch):
    expected_site = SiteFactory()
    courses = [CourseOverviewFactory() for i in range(3)]

    # Shoudl we track call for each course?
    def mock_populate_course_mau(site_id, course_id, month_for, force_update=False):
        assert site_id == Site.objects.get(id=site_id).id
        assert course_id

    def mock_get_course_keys_for_site(site):
        assert site == expected_site
        return [as_course_key(course.id) for course in courses]

    monkeypatch.setattr('figures.sites.get_course_keys_for_site',
                        mock_get_course_keys_for_site)
    monkeypatch.setattr('figures.tasks.populate_course_mau',
                        mock_populate_course_mau)

    figures.tasks.populate_mau_metrics_for_site(site_id=expected_site.id)


def test_populate_all_mau_single_site(transactional_db, monkeypatch):
    assert Site.objects.count() == 1
    expected_site = Site.objects.first()

    def mock_populate_mau_metrics_for_site(site_id, force_update=False):
        assert site_id == expected_site.id

    monkeypatch.setattr('figures.tasks.populate_mau_metrics_for_site',
                        mock_populate_mau_metrics_for_site)

    figures.tasks.populate_all_mau()


def test_populate_all_mau_multiple_site(transactional_db, monkeypatch):
    assert Site.objects.count() == 1
    sites = [Site.objects.first()]
    sites += [SiteFactory() for i in range(3)]
    sites_visited = []

    def mock_populate_mau_metrics_for_site(site_id, force_update=False):
        sites_visited.append(site_id)

    monkeypatch.setattr('figures.tasks.populate_mau_metrics_for_site',
                        mock_populate_mau_metrics_for_site)

    figures.tasks.populate_all_mau()

    assert set(sites_visited) == set([site.id for site in sites])


def test_populate_monthly_metrics_for_site(transactional_db, monkeypatch):
    """
    Simple test to exercise the figures task
    """
    expected_site = SiteFactory()
    sites_visited = []

    def mock_fill_last_smm_month(site):
        assert site == expected_site
        sites_visited.append(site)

    monkeypatch.setattr('figures.tasks.fill_last_smm_month',
                        mock_fill_last_smm_month)
    figures.tasks.populate_monthly_metrics_for_site(expected_site.id)

    assert set(sites_visited) == set([expected_site])


@pytest.mark.xfail
def test_run_figures_monthly_metrics(transactional_db, monkeypatch):
    """
    Need to add mock to call the .delay() for the subtask
    """
    expected_site = SiteFactory()
    sites_visited = []

    def mock_populate_monthly_metrics_for_site(site_id):
        assert site_id == expected_site.id
        sites_visited.append(site_id)

    monkeypatch.setattr('figures.tasks.populate_monthly_metrics_for_site',
                        mock_populate_monthly_metrics_for_site)

    figures.tasks.run_figures_monthly_metrics()
    assert set(sites_visited) == set([expected_site.id])
