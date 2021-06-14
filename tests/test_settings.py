'''Tests figures.settings

These are currently just simple tests that make sure the basics are working.
They could use elaboration to make sure that the individual settings within
each of the Figures entries to ``WEBPACK_LOADER`` and ``CELERYBEAT_SCHEDULE``
are correctly assigned
'''

from __future__ import absolute_import
import mock
import pytest


from figures import helpers as figures_helpers
from figures.settings.lms_production import plugin_settings


@pytest.mark.parametrize('features, expected', [
        ({'FIGURES_IS_MULTISITE': True}, True),
        ({'FIGURES_IS_MULTISITE': False}, False),
        ({}, False),
    ])
def test_is_multisite(features, expected):
    """
    Test features work properly for Figures multisite settings
    """
    with mock.patch('figures.helpers.settings.FEATURES', features):
        assert figures_helpers.is_multisite() == expected


@pytest.mark.parametrize('features, expected', [
        ({'FIGURES_LOG_PIPELINE_ERRORS_TO_DB': True}, True),
        ({'FIGURES_LOG_PIPELINE_ERRORS_TO_DB': False}, False),
    ])
def test_log_pipeline_errors_to_db_true(features, expected):
    with mock.patch('figures.helpers.settings.FEATURES', features):
        assert figures_helpers.log_pipeline_errors_to_db() == expected


class TestUpdateSettings(object):
    '''
    figures.settings.update_settings is a convenience method that wraps
    around:

    ::

        figures.settings.update_webpack_loader
        figures.settings.update_celerybeat_schedule

    '''
    CELERY_TASK_NAME = 'figures-populate-daily-metrics'

    def validate_webpack_loader_settings(self, webpack_loader_settings):
        assert 'FIGURES_APP' in webpack_loader_settings
        for key in ['BUNDLE_DIR_NAME', 'STATS_FILE']:
            assert key in webpack_loader_settings['FIGURES_APP']

    def validate_celerybeat_schedule_settings(self, celerybeat_schedule_settings):
        assert self.CELERY_TASK_NAME in celerybeat_schedule_settings
        for key in ['task', 'schedule']:
            assert key in celerybeat_schedule_settings['figures-populate-daily-metrics']

    @pytest.mark.parametrize('figures_env_tokens, run_celery,', [
        ({}, True),
        ({'ENABLE_DAILY_METRICS_IMPORT': True}, True),
        ({'ENABLE_DAILY_METRICS_IMPORT': False}, False),
    ])
    def test_update_settings(self, figures_env_tokens, run_celery):
        '''

        '''
        settings = mock.Mock(
            WEBPACK_LOADER={},
            CELERYBEAT_SCHEDULE={},
            FEATURES={},
            ENV_TOKENS={
                'FIGURES': figures_env_tokens,
            },
            CELERY_IMPORTS=[],
        )
        plugin_settings(settings)

        self.validate_webpack_loader_settings(settings.WEBPACK_LOADER)

        if run_celery:
            self.validate_celerybeat_schedule_settings(settings.CELERYBEAT_SCHEDULE)
        else:
            assert self.CELERY_TASK_NAME not in settings.CELERYBEAT_SCHEDULE

        assert settings.ENV_TOKENS['FIGURES'] == figures_env_tokens


class TestDailyMauPipelineSettings(object):
    """Tests MAU pipeline settings

    See how edx-platforms does plugins. App: openedx.core.djangoapps.plugins

    * constants.PLUGIN_APP_SETTINGS_FUNC_NAME
    * openedx.core.djangoapps.plugins.plugin_settings

    TODO: Abstract the core functionality in this test class because it presents
    a pattern for testing plugin CeleryBeat schedule settings
    """
    TASK_NAME = 'figures-daily-mau'
    TASK_FUNC = 'figures.tasks.populate_all_mau'

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.settings = mock.Mock(
            WEBPACK_LOADER={},
            CELERYBEAT_SCHEDULE={},
            FEATURES={},
            ENV_TOKENS={},
            CELERY_IMPORTS=[],
        )

    def test_daily_mau_pipeline_flag_enabled(self):
        self.settings.ENV_TOKENS['FIGURES'] = { 'ENABLE_DAILY_MAU_IMPORT': True }
        plugin_settings(self.settings)
        assert self.TASK_NAME in self.settings.CELERYBEAT_SCHEDULE
        assert set(['task', 'schedule', 'options']) == set(
            self.settings.CELERYBEAT_SCHEDULE[self.TASK_NAME].keys())

    def test_daily_mau_pipeline_flag_disabled(self):
        self.settings.ENV_TOKENS['FIGURES'] = { 'ENABLE_DAILY_MAU_IMPORT': False }
        plugin_settings(self.settings)
        assert self.TASK_NAME not in self.settings.CELERYBEAT_SCHEDULE

    def test_daily_mau_pipeline_flag_not_present(self):
        assert 'FIGURES' not in self.settings.ENV_TOKENS
        plugin_settings(self.settings)
        assert self.TASK_NAME not in self.settings.CELERYBEAT_SCHEDULE
