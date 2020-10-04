"""Test Figures Django management commands
"""

from __future__ import absolute_import
import mock
import pytest
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from tests.factories import SiteFactory
from tests.helpers import OPENEDX_RELEASE, GINKGO


class PopulateFiguresMetricsTest(TestCase):

    @pytest.mark.skipif(OPENEDX_RELEASE == GINKGO,
                        reason='Broken test. Apparent Django 1.8 incompatibility')
    def test_command_output(self):
        out = StringIO()
        call_command('populate_figures_metrics', '--no-delay', stdout=out)

        self.assertEqual('', out.getvalue())


def test_mau_no_delay(transactional_db):
    """
    We test that `populate_figures_metrics` command executes the method,
    `figures.tasks.populate_all_mau` in immediate mode "no delay"
    """
    path = 'figures.management.commands.populate_figures_metrics.populate_all_mau'
    with mock.patch(path) as mock_populate_all_mau:
        call_command('populate_figures_metrics', '--no-delay', '--mau')
        mock_populate_all_mau.assert_called()


def test_backfill(transactional_db):
    """Minimal test the backfill management command
    """
    path = 'figures.management.commands.backfill_figures_metrics.backfill_monthly_metrics_for_site'
    with mock.patch(path) as mock_backfill:
        call_command('backfill_figures_metrics')
        mock_backfill.assert_called()
