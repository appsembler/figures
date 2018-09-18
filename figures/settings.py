'''
This module provides default values for running Figures.

'''
import datetime
import os

from celery.schedules import crontab

from django.conf import settings as django_settings

# Specity the 'figures' package directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Define our webpack asset bundling constants
WEBPACK_BUNDLE_DIR_NAME = 'figures_bundles/'
WEBPACK_STATS_FILE = os.path.abspath(
    os.path.join(APP_DIR, '../frontend/webpack-stats.json'))

# This will raise an AttributeError if WEBPACK_LOADER is not defined in settings
# We'll just let it fail
django_settings.WEBPACK_LOADER.update(FIGURES_APP={
    'BUNDLE_DIR_NAME': WEBPACK_BUNDLE_DIR_NAME,
    'STATS_FILE': WEBPACK_STATS_FILE
    })

FIGENV_SETTINGS = django_settings.ENV_TOKENS.get('FIGURES', {})

DEFAULT_PAGINATION_LIMIT = 20


###
### Initial implementation for the Figures pipeline job sche
###
###

# Add Figures settings here. These are for Figures operational defaults
FIGURES = {
    'APP_DIR': APP_DIR,
    # Default to enable the scheduler unless settings explicitely say no
    'ENABLE_DAILY_METRICS_IMPORT': FIGENV_SETTINGS.get('ENABLE_DAILY_METRICS_IMPORT', True),
    'DAILY_METRICS_IMPORT_HOUR': FIGENV_SETTINGS.get('DAILY_METRICS_IMPORT_HOUR', 2),
    'DAILY_METRICS_IMPORT_MINUTE': FIGENV_SETTINGS.get('DAILY_METRICS_IMPORT_MINUTE', 0),
}


if FIGURES['ENABLE_DAILY_METRICS_IMPORT']:
    django_settings.CELERYBEAT_SCHEDULE['figures-populate-daily-metrics'] = {
        'task': 'figures.tasks.populate_daily_metrics',
        'schedule': crontab(
            hour=FIGURES['DAILY_METRICS_IMPORT_HOUR'],
            minute=FIGURES['DAILY_METRICS_IMPORT_MINUTE'],
            ),
        }
