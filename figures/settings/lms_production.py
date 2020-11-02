"""
Settings overrides for Figures in LMS/Production (aka AWS).
"""
from __future__ import absolute_import
import os
from celery.schedules import crontab


def update_webpack_loader(webpack_loader_settings, figures_env_tokens):
    """
    Update the WEBPACK_LOADER in the settings.
    """
    # Specify the 'figures' package directory
    figures_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Define our webpack asset bundling constants
    # TODO: https://appsembler.atlassian.net/browse/RED-673
    webpack_stats_file = figures_env_tokens.get('WEBPACK_STATS_FILE', 'webpack-stats.json')
    webpack_stats_full_path = os.path.abspath(os.path.join(figures_app_dir, webpack_stats_file))
    webpack_loader_settings.update(FIGURES_APP={
        'BUNDLE_DIR_NAME': 'figures/',
        'STATS_FILE': webpack_stats_full_path,
    })


def update_celerybeat_schedule(celerybeat_schedule_settings, figures_env_tokens):
    """
    Figures pipeline job schedule configuration in CELERYBEAT_SCHEDULE.

    Daily metrics pipeline scheduler is on by default
    Course MAU metrics pipeline scheduler is off by default

    TODO: Language improvement: Change the "IMPORT" to "CAPTURE" or "EXTRACT"
    """
    if figures_env_tokens.get('ENABLE_DAILY_METRICS_IMPORT', True):
        celerybeat_schedule_settings['figures-populate-daily-metrics'] = {
            'task': 'figures.tasks.populate_daily_metrics',
            'schedule': crontab(
                hour=figures_env_tokens.get('DAILY_METRICS_IMPORT_HOUR', 2),
                minute=figures_env_tokens.get('DAILY_METRICS_IMPORT_MINUTE', 0),
                ),
            }

    if figures_env_tokens.get('ENABLE_DAILY_MAU_IMPORT', False):
        celerybeat_schedule_settings['figures-daily-mau'] = {
            'task': 'figures.tasks.populate_all_mau',
            'schedule': crontab(
                hour=figures_env_tokens.get('DAILY_MAU_IMPORT_HOUR', 0),
                minute=figures_env_tokens.get('DAILY_MAU_IMPORT_MINUTE', 0),
                ),
            }

    if figures_env_tokens.get('ENABLE_FIGURES_MONTHLY_METRICS', True):
        celerybeat_schedule_settings['figures-monthly-metrics'] = {
            'task': 'figures.tasks.run_figures_monthly_metrics',
            'schedule': crontab(0, 0, day_of_month=1),
            }


def plugin_settings(settings):
    """
    Update the LMS/Production (aka AWS) settings to use Figures properly.


    Adds entries to the environment settings

    You can disable CeleryBeat scheduler for Figures by configuration the
    ``lms.env.json`` file.

    Create or update ``FIGURES`` as a top level key in
    the ``lms.env.json`` file:

    ::

        "FIGURES": {
            "ENABLE_DAILY_METRICS_IMPORT": false
        },

    """
    settings.ENV_TOKENS.setdefault('FIGURES', {})
    update_webpack_loader(settings.WEBPACK_LOADER, settings.ENV_TOKENS['FIGURES'])
    update_celerybeat_schedule(settings.CELERYBEAT_SCHEDULE, settings.ENV_TOKENS['FIGURES'])

    settings.CELERY_IMPORTS += (
        "figures.tasks",
    )
