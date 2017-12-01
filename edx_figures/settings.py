'''
This module provides default values for running edx-figures

'''
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

print('!!! edx-figures APP_DIR = {}'.format(APP_DIR))

# Mapping to create settings root level keys
ENV_KEYS = [
    {
        'file': 'lms.env.json',
        'key': 'EDX_FIGURES',
    }
]

EDX_FIGURES = {
    'DEFAULT_REPORT_ENCODING': 'utf-8',
    'REPORT_ROW_BUILDERS': {
        'learners': 'edx_figures.builders.DemographicReportRowBuilder',
        'grades': 'edx_figures.builders.GradeReportRowBuilder',
    }
}

webpack_bundle_dir_name = 'edx_figures_bundles/'
webpack_stats_file = os.path.abspath(os.path.join(APP_DIR, 'webpack-stats.json'))

staticfiles_dir = os.path.join(APP_DIR, 'assets')