"""Test figures.tasks Daily task functions

# Overview of daily pipeline

Figures daily pipeline collects and aggregates data from Open edX (edx-platform)
into Figures models.

The Figures task functions are Celery tasks. However currently only the top
level task function is called asynchronously.

# Daily pipeline execution

The daily pipeline executes at the following levels

1. Top level initiates the daily metrics collection job. It iterates over each
   site to be processed (currently all sites)
2. Per site execution. It iterates over each course in the site. After all the
   courses have been processed, Figures `EnrollmentData` are updated
3. Per course execution. It iterates over each enrollment in the course
4. Per enrollment exeuction. It processes per enrollment (learner + course pair)

These are the functions called, the purpose and details

1. 'populate_daily_metrics'

* Gets list (queryset) of Site objects
* Iterates over each site and calls 'populate_daily_metrics_for_site' for each
  site

2. 'populate_daily_metrics_for_site'

* Gets list (queryset) of course id strings for the site
* Iterates over each course id and calls 'populate_single_cdm' for each course
* After all the CourseDailyMetrics records have been collected, calls
  'populate_single_sdm'

3. 'populate_single_sdm'

* Fills the SiteDailyMetrics record for the site + date pair

4. 'populate_single_cdm'

* Fills the CourseDailyMetrics record for the specified course

5. 'update_enrollment_data'

* Updates Figures 'EnrollmentData' records. These records provide a current
  snapshot of enrollment data

# Testing priorities

We have two top priorities for this testing module:

1. Verify nominal operation will work
2. Verify failures at one level do not cause any of the levels above to fail

Of secondary importance is testing log output
"""
from __future__ import absolute_import
from datetime import date
import logging
import pytest
from six.moves import range
from django.contrib.sites.models import Site
from waffle.testutils import override_switch

from figures.helpers import as_date, as_datetime
from figures.models import (CourseDailyMetrics,
                            SiteDailyMetrics)

from figures.tasks import (FPD_LOG_PREFIX,
                           populate_single_cdm,
                           populate_single_sdm,
                           populate_daily_metrics_for_site,
                           populate_daily_metrics)
from tests.factories import (CourseDailyMetricsFactory,
                             CourseOverviewFactory,
                             SiteDailyMetricsFactory,
                             SiteFactory)
from tests.helpers import OPENEDX_RELEASE, GINKGO, FakeException


def test_populate_single_cdm(transactional_db, monkeypatch):
    """Test figures.tasks.populate_single_cdm nominal case

    This tests the normal execution to popluate a single CourseDailyMetrics
    record
    """
    assert CourseDailyMetrics.objects.count() == 0
    date_for = '2019-01-02'
    course_id = "course-v1:certs-appsembler+001+2019"
    created = False

    def mock_cdm_load(self, date_for, **kwargs):
        return (CourseDailyMetricsFactory(date_for=date_for), created, )

    monkeypatch.setattr('figures.sites.get_site_for_course',
                        lambda val: SiteFactory())
    monkeypatch.setattr(
        'figures.pipeline.course_daily_metrics.CourseDailyMetricsLoader.load',
        mock_cdm_load)

    populate_single_cdm(course_id, date_for)

    assert CourseDailyMetrics.objects.count() == 1
    assert as_date(CourseDailyMetrics.objects.first().date_for) == as_date(date_for)


@pytest.mark.django_db
def test_disable_populate_daily_metrics(caplog):
    """Test figures.tasks.populate_daily_metrics

    Tests that when WAFFLE_DISABLE_PIPELINE is active, the disabled warning msg is logged
    """
    with override_switch('figures.disable_pipeline', active=True):
        populate_daily_metrics()
        assert 'disabled' in caplog.text


@pytest.mark.django_db
def test_enable_populate_daily_metrics(caplog):
    """Test figures.tasks.populate_daily_metrics

    Tests that when WAFFLE_DISABLE_PIPELINE is not active, the disabled warning msg is not logged
    """
    with override_switch('figures.disable_pipeline', active=False):
        populate_daily_metrics()
        assert 'disabled' not in caplog.text


def test_populate_single_sdm(transactional_db, monkeypatch):
    """Test figures.tasks.populate_single_sdm

    Test the task function that fills the SiteDailyMetrics record for a given
    site
    """
    assert SiteDailyMetrics.objects.count() == 0
    date_for = '2019-01-02'
    created = False
    site = SiteFactory()

    def mock_sdm_load(self, site, date_for, **kwargs):
        return (SiteDailyMetricsFactory(site=site), created, )

    monkeypatch.setattr(
        'figures.pipeline.site_daily_metrics.SiteDailyMetricsLoader.load',
        mock_sdm_load)

    populate_single_sdm(site.id, date_for=date_for)

    assert SiteDailyMetrics.objects.count() == 1


@pytest.mark.parametrize('date_for', [
    '2020-12-12',
    as_date('2020-12-12'),
    as_datetime('2020-12-12')
])
def test_populate_daily_metrics_for_site_basic(transactional_db,
                                               monkeypatch,
                                               date_for):
    site = SiteFactory()
    course_ids = ['fake-course-1', 'fake-course-2']
    collected_course_ids = []

    def fake_populate_single_cdm(course_id, **_kwargs):
        collected_course_ids.append(course_id)

    def fake_populate_single_sdm(site_id, **_kwargs):
        assert site_id == site.id

    monkeypatch.setattr('figures.tasks.site_course_ids', lambda site: course_ids)
    monkeypatch.setattr('figures.tasks.populate_single_cdm',
                        fake_populate_single_cdm)
    monkeypatch.setattr('figures.tasks.populate_single_sdm',
                        fake_populate_single_sdm)

    populate_daily_metrics_for_site(site_id=site.id, date_for=date_for)
    assert set(collected_course_ids) == set(course_ids)


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO,
                    reason='Apparent Django 1.8 incompatibility')
def test_populate_daily_metrics_for_site_error_on_cdm(transactional_db,
                                                      monkeypatch,
                                                      caplog):

    date_for = date.today()
    site = SiteFactory()
    fake_course_ids = ['fake-course-id-1']

    def fake_pop_single_cdm_fails(**kwargs):
        # TODO: test with different exceptions
        # At least one with and without `message_dict`
        raise FakeException('Hey!')

    monkeypatch.setattr('figures.tasks.site_course_ids',
                        lambda site: fake_course_ids)
    monkeypatch.setattr('figures.tasks.populate_single_cdm',
                        fake_pop_single_cdm_fails)

    populate_daily_metrics_for_site(site_id=site.id, date_for=date_for)

    last_log = caplog.records[-1]
    expected_msg = ('{prefix}:SITE:COURSE:FAIL:populate_daily_metrics_for_site. '
                    'site_id:{site_id}, date_for:{date_for}. '
                    'course_id:{course_id} exception:{exception}'
                    ).format(prefix=FPD_LOG_PREFIX,
                             site_id=site.id,
                             date_for=date_for,
                             course_id=fake_course_ids[0],
                             exception='Hey!')
    assert last_log.message == expected_msg


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO,
                    reason='Apparent Django 1.8 incompatibility')
def test_populate_daily_metrics_for_site_site_dne(transactional_db,
                                                  monkeypatch,
                                                  caplog):
    """
    If there is an invalid site id, logs error and raises it
    """
    bad_site_id = Site.objects.order_by('id').last().id + 1
    date_for = date.today()
    assert not Site.objects.filter(id=bad_site_id).exists()

    with pytest.raises(Exception) as e:
        populate_daily_metrics_for_site(site_id=bad_site_id, date_for=date_for)

    assert str(e.value) == 'Site matching query does not exist.'
    last_log = caplog.records[-1]
    expected_message = ('FIGURES:PIPELINE:DAILY:SITE:FAIL:'
                        'populate_daily_metrics_for_site:site_id: {} does not exist')
    assert last_log.message == expected_message.format(bad_site_id)


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO,
                    reason='Apparent Django 1.8 incompatibility')
def test_populate_daily_metrics_site_level_error(transactional_db,
                                                 monkeypatch,
                                                 caplog):
    """
    Generic test that the first site fails but we can process the second site
    """
    assert Site.objects.count() == 1  # Because we always have 'example.com'

    good_site = Site.objects.first()
    bad_site = SiteFactory()
    populated_site_ids = []
    failed_site_ids = []
    date_for = date.today()

    def fake_populate_daily_metrics_for_site(site_id, **_kwargs):
        """
        """
        if site_id == bad_site.id:
            failed_site_ids.append(site_id)
            raise FakeException('Hey!')
        else:
            populated_site_ids.append(site_id)

    monkeypatch.setattr('figures.tasks.populate_daily_metrics_for_site',
                        fake_populate_daily_metrics_for_site)

    populate_daily_metrics(date_for=date_for)
    assert set(populated_site_ids) == set([good_site.id])
    assert set(failed_site_ids) == set([bad_site.id])

    last_log = caplog.records[-1]
    expected_msg = ('{prefix}:FAIL populate_daily_metrics unhandled site level'
                    ' exception for site[{site_id}]={domain}').format(
                    prefix=FPD_LOG_PREFIX,
                    site_id=bad_site.id,
                    domain=bad_site.domain)
    assert last_log.message == expected_msg

# TODO: def test_populate_daily_metrics_future_date_error


@pytest.mark.skipif(OPENEDX_RELEASE == GINKGO,
                    reason='Apparent Django 1.8 incompatibility')
def test_populate_daily_metrics_enrollment_data_error(transactional_db,
                                                      monkeypatch,
                                                      caplog):
    # Needs to be 'today' so that enrollment data update gets called
    date_for = date.today()
    site = SiteFactory()

    def fake_populate_daily_metrics_for_site(**_kwargs):
        pass

    def fake_update_enrollment_data_fails(**kwargs):
        # TODO: test with different exceptions
        # At least one with and without `message_dict`
        raise FakeException('Hey!')

    monkeypatch.setattr('figures.tasks.populate_daily_metrics_for_site',
                        fake_populate_daily_metrics_for_site)
    monkeypatch.setattr('figures.tasks.update_enrollment_data',
                        fake_update_enrollment_data_fails)

    populate_daily_metrics(date_for=date_for)

    last_log = caplog.records[-1]
    expected_msg = ('{prefix}:FAIL figures.tasks update_enrollment_data '
                    ' unhandled exception. site[{site_id}]:{domain}').format(
                    prefix=FPD_LOG_PREFIX,
                    site_id=site.id,
                    domain=site.domain)
    assert last_log.message == expected_msg


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

        populate_daily_metrics(date_for=date_for)
