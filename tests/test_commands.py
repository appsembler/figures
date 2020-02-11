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


def test_mau_no_delay(monkeypatch):
    """
    We test that `populate_figures_metrics` command executes the method,
    `figures.tasks.populate_all_mau` in immediate mode "no delay"

    Tried to use `mock.patch` on the following:
        'figures.management.commands.populate_figures_metrics.populate_all_mau'
    See the test function`test_mau_no_delay_with_mock` below for details
    """
    call_list = []

    def mock_populate_all_mau():
        """Mocks the function `figures.tasks.populate_all_mau`

        The function `populate_all_mau` does not return a value, so we modify a
        variable in our parent test function to assert that the mock method was
        called. Because of Python's inner function scoping rules, we can read
        but cannot change them. However, this seems limited to instance variables.
        Reference variables appear to not have this limitation. Therefore, we
        append to a list in our outer function.
        """
        call_list.append(True)

    path = 'figures.management.commands.populate_figures_metrics.populate_all_mau'
    monkeypatch.setattr(path, mock_populate_all_mau)
    call_command('populate_figures_metrics', '--no-delay', '--mau')
    assert len(call_list) == 1


@pytest.mark.skip('This test does not work')
def test_mau_no_delay_with_mock(transactional_db):
    """
    This would be the preferred test to the above. Acccording to the documentation,
    this should work, but the mock never gets called, so something is not right

    https://docs.python.org/dev/library/unittest.mock.html#where-to-patch
    """
    path = 'figures.management.commands.populate_figures_metrics.populate_all_mau'
    with mock.patch(path) as mock_populate_all_mau:
        call_command('populate_figures_metrics', '--no-delay')
        mock_populate_all_mau.assert_called()
