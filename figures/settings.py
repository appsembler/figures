'''
This module provides default values for running Figures.

We need to add Figures to ``WEBPACK_LOADER`` and ``CELERYBEAT_SCHEDULE``

So we're injecting them here to minimze customizations needed in edx-platform's
settings

'''
import os

from celery.schedules import crontab

from django.conf import settings as django_settings

# Specity the 'figures' package directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))

FIGENV_SETTINGS = django_settings.ENV_TOKENS.get('FIGURES', {})

# Define our webpack asset bundling constants
WEBPACK_BUNDLE_DIR_NAME = 'figures/'
WEBPACK_STATS_FILE = FIGENV_SETTINGS.get(
    'WEBPACK_STATS_FILE', 'webpack-stats.json')
WEBPACK_STATS_FULL_PATH = os.path.abspath(
    os.path.join(APP_DIR, WEBPACK_STATS_FILE))

# This will raise an AttributeError if WEBPACK_LOADER is not defined in settings
# We'll just let it fail
django_settings.WEBPACK_LOADER.update(FIGURES_APP={
    'BUNDLE_DIR_NAME': WEBPACK_BUNDLE_DIR_NAME,
    'STATS_FILE': WEBPACK_STATS_FULL_PATH,
    })

# How many records the Figures REST API will return on a page by default
DEFAULT_PAGINATION_LIMIT = 20


# Add Figures settings here. These are for Figures operational defaults
# TODO: Add the webpack settings here
FIGURES = {
    'APP_DIR': APP_DIR,
    # Default to enable the scheduler unless settings explicitely say no
    'ENABLE_DAILY_METRICS_IMPORT': FIGENV_SETTINGS.get('ENABLE_DAILY_METRICS_IMPORT', True),
    'DAILY_METRICS_IMPORT_HOUR': FIGENV_SETTINGS.get('DAILY_METRICS_IMPORT_HOUR', 2),
    'DAILY_METRICS_IMPORT_MINUTE': FIGENV_SETTINGS.get('DAILY_METRICS_IMPORT_MINUTE', 0),
}


#
# Initial implementation for the Figures pipeline job sche
#


if FIGURES['ENABLE_DAILY_METRICS_IMPORT']:
    django_settings.CELERYBEAT_SCHEDULE['figures-populate-daily-metrics'] = {
        'task': 'figures.tasks.populate_daily_metrics',
        'schedule': crontab(
            hour=FIGURES['DAILY_METRICS_IMPORT_HOUR'],
            minute=FIGURES['DAILY_METRICS_IMPORT_MINUTE'],
            ),
        }
