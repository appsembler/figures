'''Test Figures Django management commands

'''

from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

class PopulateFiguresMetricsTest(TestCase):
    def test_command_output(self):
        out = StringIO()
        call_command('populate_figures_metrics', '--no-delay', stdout=out)

        self.assertEqual('', out.getvalue())
        #self.assertIn('Expected output', out.getvalue())