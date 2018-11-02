"""
This module provides default values for running Figures along with functions to
add entries to the Django conf settings needed to run Figures.

"""

import copy
import os
import sys

from celery.schedules import crontab

# Declare How many records the Figures REST API will return on a page by default
DEFAULT_PAGINATION_LIMIT = 20

DAILY_METRICS_CELERY_TASK_LABEL = 'figures-populate-daily-metrics'

DEFAULT_LOG_PIPELINE_ERRORS_TO_DB = True

env_tokens = {}


def log_pipeline_errors_to_db():
    """Capture pipeline errors to the figures.models.PipelineError model
    """
    return bool(env_tokens.get('LOG_PIPELINE_ERRORS_TO_DB',
                               DEFAULT_LOG_PIPELINE_ERRORS_TO_DB))


def update_webpack_loader(webpack_loader_settings, figures_env_tokens=None):
    """
    figures_env_tokens is a dict retrieved from the ``ENV_TOKENS`` in the LMS
    settings

    ::

        django.conf.settings.ENV_TOKENS.get('FIGURES', {})

    """
    # Specify the 'figures' package directory
    app_dir = os.path.dirname(os.path.abspath(__file__))

    if not figures_env_tokens:
        figures_env_tokens = {}

    # Define our webpack asset bundling constants
    webpack_stats_file = figures_env_tokens.get(
        'WEBPACK_STATS_FILE', 'webpack-stats.json')
    webpack_stats_full_path = os.path.abspath(
        os.path.join(app_dir, webpack_stats_file))
    webpack_loader_settings.update(FIGURES_APP={
        'BUNDLE_DIR_NAME': 'figures/',
        'STATS_FILE': webpack_stats_full_path,
    })


def update_celerybeat_schedule(celerybeat_schedule_settings, figures_env_tokens=None):
    """Initial implementation for the Figures pipeline job schedule configuration

    """
    if not figures_env_tokens:
        figures_env_tokens = {}

    celerybeat_schedule_settings[DAILY_METRICS_CELERY_TASK_LABEL] = {
        'task': 'figures.tasks.populate_daily_metrics',
        'schedule': crontab(
            hour=figures_env_tokens.get('DAILY_METRICS_IMPORT_HOUR', 2),
            minute=figures_env_tokens.get('DAILY_METRICS_IMPORT_MINUTE', 0),
            ),
        }


def update_env_tokens(figures_env_tokens):
    """Captures Figures settings declared in the ``lms.env.json`` file

    This is used to allow configuration driven behavior in Figures
    """
    thismodule = sys.modules[__name__]
    setattr(thismodule, 'env_tokens', copy.deepcopy(figures_env_tokens))


def update_settings(webpack_loader_settings,
                    celerybeat_schedule_settings,
                    figures_env_tokens):
    """Adds entries to the environment settings
    This is a convenience method that calls the following:

    ::

        figures.settings.update_webpack_loader
        figures.settings.update_celerybeat_schedule

    You can disable CeleryBeat scheduler for Figures by configuration the
    ``lms.env.json`` file. Create or update ``FIGURES`` as a top level key in
    the ``lms.env.json`` file:

    ::

        "FIGURES": {
            "ENABLE_DAILY_METRICS_IMPORT": false
        },

    """
    update_webpack_loader(webpack_loader_settings, figures_env_tokens)

    enable_celerybeat_job = True
    if figures_env_tokens:
        enable_celerybeat_job = figures_env_tokens.get(
            'ENABLE_DAILY_METRICS_IMPORT', True)
    if enable_celerybeat_job:
        update_celerybeat_schedule(celerybeat_schedule_settings, figures_env_tokens)
    update_env_tokens(figures_env_tokens)
