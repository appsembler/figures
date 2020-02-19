"""Test Figures Django management commands
"""

import mock
import pytest
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO


class PopulateFiguresMetricsTest(TestCase):

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
