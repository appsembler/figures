"""

"""

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)

from figures.helpers import as_date
from figures.models import (
    CourseDailyMetrics,
    PipelineError,
    SiteDailyMetrics,
    )
import figures.tasks
import figures.mau

from tests.factories import (
    CourseDailyMetricsFactory,
    CourseOverviewFactory,
    SiteFactory,
    SiteDailyMetricsFactory,
    )


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


def test_collect_mau_metrics_for_site(transactional_db, monkeypatch):
    expected_site = SiteFactory()

    def mock_store_mau_metrics(site, overwrite=False):
        assert site

    monkeypatch.setattr('figures.tasks.store_mau_metrics', mock_store_mau_metrics)

    figures.tasks.collect_mau_metrics_for_site(expected_site.id)


def test_collect_mau_metrics(transactional_db, monkeypatch):
    """
    Very minimal test
    """
    assert Site.objects.count() == 1
    sites = [Site.objects.first()]
    sites += [SiteFactory() for i in range(3)]
    sites_visited = []

    def mock_store_mau_metrics(site, overwrite=False):
        sites_visited.append(site)

    monkeypatch.setattr('figures.tasks.store_mau_metrics', mock_store_mau_metrics)

    figures.tasks.collect_mau_metrics()

    assert set([site.id for site in sites_visited]) == set([site.id for site in sites])
