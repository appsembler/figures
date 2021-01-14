"""Test figures.tasks MAU tasks

These tasks are not currently run in production
"""
from datetime import date
from django.contrib.sites.models import Site

from figures.helpers import as_course_key
from figures.tasks import (populate_course_mau,
                           populate_mau_metrics_for_site,
                           populate_all_mau)
from tests.factories import (CourseMauMetricsFactory,
                             CourseOverviewFactory,
                             SiteFactory)


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

    populate_course_mau(site_id=expected_site.id,
                        course_id=str(course.id))
    # TODO: Create own test function
    populate_course_mau(site_id=expected_site.id,
                        course_id=str(course.id),
                        month_for=None)
    populate_course_mau(site_id=expected_site.id,
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

    populate_mau_metrics_for_site(site_id=expected_site.id)


def test_populate_all_mau_single_site(transactional_db, monkeypatch):
    assert Site.objects.count() == 1
    expected_site = Site.objects.first()

    def mock_populate_mau_metrics_for_site(site_id, force_update=False):
        assert site_id == expected_site.id

    monkeypatch.setattr('figures.tasks.populate_mau_metrics_for_site',
                        mock_populate_mau_metrics_for_site)

    populate_all_mau()


def test_populate_all_mau_multiple_site(transactional_db, monkeypatch):
    assert Site.objects.count() == 1
    sites = [Site.objects.first()]
    sites += [SiteFactory() for i in range(3)]
    sites_visited = []

    def mock_populate_mau_metrics_for_site(site_id, force_update=False):
        sites_visited.append(site_id)

    monkeypatch.setattr('figures.tasks.populate_mau_metrics_for_site',
                        mock_populate_mau_metrics_for_site)

    populate_all_mau()

    assert set(sites_visited) == set([site.id for site in sites])
