"""Test Figures Django management command, 'backfill_figures_daily_metrics'
"""
from __future__ import absolute_import
import pytest

try:
    from unittest import mock
except ImportError:
    # for Python 2.7
    import mock

from django.core.management import call_command

from figures.helpers import as_date

from tests.factories import SiteFactory


@pytest.mark.django_db
class TestBackfillDailyMetricsCommand(object):

    MANAGEMENT_COMMAND = 'backfill_figures_daily_metrics'
    CMD_FULL_PATH = 'figures.management.commands.{}'.format(MANAGEMENT_COMMAND)
    MOCK_PATH = CMD_FULL_PATH + '.backfill_daily_metrics_for_site_and_date'

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        self.site = SiteFactory()

        # What we set the mocked func to return
        self.mock_ret_val = dict(
            logfile='fale-logfile',
            courses_processed=42,
            cdms_elapsed=3.14159,
            sdm_elapsed=2.71828)

    @pytest.mark.parametrize('site_identifier', ['domain', 'id'])
    def test_one_day(self, monkeypatch, site_identifier):
        """Run command for single site and date
        """

        # What we pass as CLI kwargs
        cmd_kwargs = dict(
            date='2021-03-15',
            skip_sdm=False,
            force_update=False,
            logdir=None)

        # What we expect to be passed to the pipeline.bakfill function as kwargs
        expected_kwargs = dict(
            process_sdm=True,
            logdir=None,
            force_update=False)

        with mock.patch(self.MOCK_PATH) as mock_func:
            mock_func.resturn_value = self.mock_ret_val
            call_command(self.MANAGEMENT_COMMAND,
                         str(getattr(self.site, site_identifier)),
                         **cmd_kwargs)
            mock_func.assert_called_once_with(self.site,
                                              as_date(cmd_kwargs['date']),
                                              **expected_kwargs)

    @pytest.mark.parametrize('site_identifier', ['domain', 'id'])
    def test_date_range(self, monkeypatch, site_identifier):
        """Run command with start and end date range
        """

        # What we pass as CLI kwargs
        cmd_kwargs = dict(
            date_range=['2021-03-15', '2021-03-17'],
            skip_sdm=False,
            force_update=False,
            logdir=None)

        # What we expect to be passed to the pipeline.bakfill function as kwargs
        expected_kwargs = dict(
            process_sdm=True,
            logdir=None,
            force_update=False)

        expected_calls = [
            mock.call(self.site, as_date('2021-03-15'), **expected_kwargs),
            mock.call(self.site, as_date('2021-03-16'), **expected_kwargs),
            mock.call(self.site, as_date('2021-03-17'), **expected_kwargs),
        ]

        with mock.patch(self.MOCK_PATH) as mock_func:
            mock_func.return_value = self.mock_ret_val
            call_command(self.MANAGEMENT_COMMAND,
                         str(getattr(self.site, site_identifier)),
                         **cmd_kwargs)
            mock_func.assert_has_calls(expected_calls)
