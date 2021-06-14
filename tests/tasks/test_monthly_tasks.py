"""Test figures.tasks monthly job tasks

Test functions are named 'test_<function_name>_<condition>'

if '_<condition>' is absent, it means this is a basic 'happy scenario' test case
"""
import pytest
from django.contrib.sites.models import Site
from figures.tasks import (FPM_LOG_PREFIX,
                           populate_monthly_metrics_for_site,
                           run_figures_monthly_metrics)

from tests.factories import SiteFactory
from tests.helpers import OPENEDX_RELEASE, GINKGO, FakeException


def test_populate_monthly_metrics_for_site(transactional_db, monkeypatch):
    """Verify with basic test case
    """
    expected_site = SiteFactory()
    sites_visited = []

    def fake_fill_last_smm_month(site):
        assert site == expected_site
        sites_visited.append(site)

    monkeypatch.setattr('figures.tasks.fill_last_smm_month',
                        fake_fill_last_smm_month)

    populate_monthly_metrics_for_site(expected_site.id)

    assert set(sites_visited) == set([expected_site])


def test_populate_monthly_metrics_for_site_does_not_exist(transactional_db,
                                                          monkeypatch,
                                                          caplog):
    """Verify an error is logged  for invalid site id
    """
    site_id = 9999
    assert not Site.objects.filter(id=site_id).exists()

    populate_monthly_metrics_for_site(site_id)

    last_log = caplog.records[-1]
    expected_log = (
        '{prefix}:SITE:ERROR: site_id:{site_id} Site does not exist').format(
        prefix=FPM_LOG_PREFIX,
        site_id=site_id)
    assert last_log.message == expected_log


def test_populate_monthly_metrics_for_site_other_error(transactional_db,
                                                       monkeypatch,
                                                       caplog):
    """Verify an error is loged for general exception
    """
    expected_site = SiteFactory()

    def fake_fill_last_smm_month(site):
        raise FakeException('Hey!')

    monkeypatch.setattr('figures.tasks.fill_last_smm_month',
                        fake_fill_last_smm_month)

    populate_monthly_metrics_for_site(expected_site.id)

    last_log = caplog.records[-1]
    expected_log = (
        '{prefix}:SITE:ERROR: site_id:{site_id} Other error').format(
        prefix=FPM_LOG_PREFIX,
        site_id=expected_site.id)
    assert last_log.message == expected_log


def test_run_figures_monthly_metrics_with_faked_subtask(transactional_db, monkeypatch):
    """Verify we visit the site in the subtask

    Faking the subtask for the function under test
    """
    expected_sites = Site.objects.all()
    assert expected_sites
    sites_visited = []

    def fake_populate_monthly_metrics_for_site(celery_task_group):
        for t in celery_task_group.tasks:
            sites_visited.extend(t.args)

    monkeypatch.setattr('celery.group.delay', fake_populate_monthly_metrics_for_site)

    run_figures_monthly_metrics()

    assert set(sites_visited) == set([rec.id for rec in expected_sites])


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO,
                    reason='Broken test. Apparent Django 1.8 incompatibility')
def test_run_figures_monthly_metrics_with_unfaked_subtask(transactional_db, monkeypatch):
    """Verify we visit the function our subtasks calls

    Faking the function called by the subtask our function under test calls.
    Basically, we're faking two levels below our function under test instead of
    one level below
    """
    expected_sites = Site.objects.all()
    assert expected_sites.count()
    sites_visited = []

    def fake_fill_last_smm_month(site):
        # assert site == expected_site
        sites_visited.append(site)

    monkeypatch.setattr('figures.tasks.fill_last_smm_month',
                        fake_fill_last_smm_month)

    run_figures_monthly_metrics()

    assert set(sites_visited) == set(expected_sites)
