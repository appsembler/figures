"""Test Figures Django management commands
"""

from __future__ import absolute_import

from dateutil import parser
import mock
import pytest

from django.contrib.sites.models import Site
from django.core.management import call_command

from figures.management.base import BaseBackfillCommand

from tests.factories import SiteFactory


@pytest.mark.django_db
class TestBaseBackfillCommand(object):
    """Exercise common backfill command base class methods."""

    @pytest.mark.parametrize('site, expected_result', [
        ('1', [1]),
        (None, [1, 2, 3]),
        ('site-1.example.com', [3]),
        ('4', []),
        ('site-88.example.com', [])
    ])
    def test_get_side_ids(self, site, expected_result):
        """Test that get_site_ids will return the correct Site id if passed that id
        or the corresponding Site's domain, will return all Site ids if none passed, 
        and will return an empty list if a non-existing Site id or domain passed
        """
        # Site table will have an existing example.com Site as well as whatever we
        # create w/ SiteFactory, due to data migration
        example_site = Site.objects.get(domain='example.com')
        SiteFactory.reset_sequence(0)
        site1 = SiteFactory()  # site-0.example.com
        site2 = SiteFactory()  # site-1.example.com
        with mock.patch('figures.management.base.get_sites') as mock_get_sites:
            mock_get_sites.return_value = [example_site, site1, site2]
            site_ids = BaseBackfillCommand().get_site_ids(site)
            assert site_ids == expected_result


@pytest.mark.django_db
class TestBackfillDailyMetrics(object):
    """Exercise backfill_figures_daily_metrics command."""

    BASE_PATH = 'figures.management.commands.backfill_figures_daily_metrics'
    PLAIN_PATH = BASE_PATH + '.populate_daily_metrics'
    DELAY_PATH = PLAIN_PATH + '.delay'
    EXP_PATH = BASE_PATH + '.experimental_populate_daily_metrics'

    def test_backfill_daily_func(self):
        """Test backfill daily regular and experimental.
        """
        with mock.patch(self.PLAIN_PATH) as mock_populate:
            call_command('backfill_figures_daily_metrics', no_delay=True)
            mock_populate.assert_called()
        with mock.patch(self.EXP_PATH) as mock_populate_exp:
            call_command('backfill_figures_daily_metrics', experimental=True, no_delay=True)
            mock_populate_exp.assert_called()

    def test_backfill_daily_delay(self):
        """Test backfill daily called without no_delay uses Celery task delay.
        """
        with mock.patch(self.DELAY_PATH) as mock_populate:
            call_command('backfill_figures_daily_metrics')
            mock_populate.assert_called()

    def test_backfill_daily_dates(self):
        """Test backfill daily called with start and end dates
        """
        end = '2021-06-08'
        start = '2021-01-01'
        start_dt = parser.parse(start)
        end_dt = parser.parse(end)
        exp_days = abs((end_dt - start_dt).days) + 1
        with mock.patch(self.PLAIN_PATH) as mock_populate:
            call_command(
                'backfill_figures_daily_metrics', 
                date_start=start, date_end=end, no_delay=True
            )
            assert mock_populate.call_count == exp_days

    def test_backfill_daily_same_day(self):
        """Test backfill daily called with same start and end date.
        """
        start = '2021-06-08'
        end = '2021-06-08'
        exp_days = 1
        with mock.patch(self.PLAIN_PATH) as mock_populate:
            call_command(
                'backfill_figures_daily_metrics', 
                date_start=start, date_end=end, no_delay=True
            )
            assert mock_populate.call_count == exp_days

    def test_backfill_daily_with_site_id(self):
        """Test that proper site id gets passed to task func when passing integer."""
        with mock.patch(self.PLAIN_PATH) as mock_populate:
            call_command('backfill_figures_daily_metrics', site=1, no_delay=True)
            assert mock_populate.called_with(site_id=1)

    def test_backfill_daily_with_site_domain(self):
        """Test that proper site id gets passed to task func when passing integer."""
        SiteFactory.reset_sequence(0)
        site2 = SiteFactory()  # site-0.example.com
        with mock.patch(self.PLAIN_PATH) as mock_populate:
            call_command('backfill_figures_daily_metrics', site="site-0.example.com", no_delay=True)
            assert mock_populate.called_with(site_id=2)

    def test_backfill_daily_without_site_id(self):
        """Test that proper site id gets passed to task func when passing integer."""
        with mock.patch(self.PLAIN_PATH) as mock_populate:
            call_command('backfill_figures_daily_metrics', no_delay=True)
            assert mock_populate.called_with(site_id=None)


class TestPopulateFiguresMetricsCommand(object):
    """Test that command gives a pending deprecation warning and that it calls the correct
    substitute management commands based on passed options.
    """

    def test_pending_deprecation(self):
        mock_call_path = 'figures.management.commands.populate_figures_metrics.call_command'
        with mock.patch(mock_call_path):
            with pytest.warns(PendingDeprecationWarning):
                call_command('populate_figures_metrics')

    @pytest.mark.parametrize('options, subst_command, subst_call_options', [
        (
            {'mau': True, 'no_delay': None, 'date': '2021-06-14', 'experimental': None},
            'run_figures_mau_metrics',
            {'no_delay': None}
        ),
        (
            {
                'mau': False, 'no_delay': True, 'date': '2021-06-14',
                'experimental': True, 'force_update': True
            },
            'backfill_figures_daily_metrics',
            {
                'no_delay': True, 'experimental': True, 'overwrite': True,
                'date_start': '2021-06-14', 'date_end': '2021-06-14'
            }
        )
    ])
    def test_correct_subtitute_commands_called(self, options, subst_command, subst_call_options):
        old_pop_cmd = 'figures.management.commands.populate_figures_metrics.call_command'
        with mock.patch(old_pop_cmd) as mock_call_cmd:
            call_command('populate_figures_metrics', **options)  # this isn't the patched version of call_command
            mock_call_cmd.assert_called_with(subst_command, **subst_call_options)


class TestBackfillFiguresMetricsCommand(object):
    """Test that command gives a pending deprecation warning and that it calls the correct
    substitute management commands based on passed options.
    """

    def test_pending_deprecation(self):
        mock_call_path = 'figures.management.commands.backfill_figures_metrics.call_command'
        with mock.patch(mock_call_path):
            with pytest.warns(PendingDeprecationWarning):
                call_command('backfill_figures_metrics')

    @pytest.mark.parametrize('options, subst_call_options', [
        (
            {'site': 1, 'overwrite': None},
            {'site': 1, 'overwrite': None}
        ),
        (
            {'overwrite': True},
            {'site': None, 'overwrite': True}
        ),
    ])
    def test_correct_subtitute_commands_called(self, options, subst_call_options):
        old_pop_cmd = 'figures.management.commands.backfill_figures_metrics.call_command'
        with mock.patch(old_pop_cmd) as mock_call_cmd:
            call_command('backfill_figures_metrics', **options)  # this isn't the patched version of call_command
            dailycmd = 'backfill_figures_daily_metrics'
            monthlycmd = 'backfill_figures_monthly_metrics'
            mock_call_cmd.assert_any_call(dailycmd, **subst_call_options)
            mock_call_cmd.assert_any_call(monthlycmd, **subst_call_options)
