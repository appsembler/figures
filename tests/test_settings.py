'''Tests figures.settings

These are currently just simple tests that make sure the basics are working.
They could use elaboration to make sure that the individual settings within
each of the Figures entries to ``WEBPACK_LOADER`` and ``CELERYBEAT_SCHEDULE``
are correctly assigned
'''

import mock
import pytest

from figures import update_settings
from figures import settings as figures_settings


@pytest.mark.parametrize('env_tokens, expected ', [
        ({'LOG_PIPELINE_ERRORS_TO_DB': True}, True),
        ({'LOG_PIPELINE_ERRORS_TO_DB': False}, False),
    ])
def test_log_pipeline_errors_to_db_true(env_tokens, expected):
    with mock.patch('figures.settings.env_tokens', env_tokens):
        assert figures_settings.log_pipeline_errors_to_db() == expected


class TestUpdateSettings(object):
    '''
    figures.settings.update_settings is a convenience method that wraps
    around:

    ::

        figures.settings.update_webpack_loader
        figures.settings.update_celerybeat_schedule

    '''
    def setup(self):
        self.webpack_loader_settings = {}
        self.celerybeat_schedule_settings = {}
        self.celery_task_name = figures_settings.DAILY_METRICS_CELERY_TASK_LABEL

    def test_update_in_package_init(self):
        '''Make sure that the ``update_settings`` method in the package init
        module is the same as in ``figures.settings``
        '''
        assert update_settings == figures_settings.update_settings

    def validate_webpack_loader_settings(self):
        assert 'FIGURES_APP' in self.webpack_loader_settings
        for key in ['BUNDLE_DIR_NAME', 'STATS_FILE']:
            assert key in self.webpack_loader_settings['FIGURES_APP']

    def validate_celerybeat_schedule_settings(self):
        assert self.celery_task_name in self.celerybeat_schedule_settings
        for key in ['task', 'schedule']:
            assert key in self.celerybeat_schedule_settings['figures-populate-daily-metrics']

    @pytest.mark.parametrize('figures_env_tokens, run_celery,', [
        (None, True),
        ({}, True),
        ({'ENABLE_DAILY_METRICS_IMPORT': True}, True),
        ({'ENABLE_DAILY_METRICS_IMPORT': False}, False),
    ])
    def test_update_settings(self, figures_env_tokens, run_celery):
        '''

        '''
        figures_settings.env_tokens = dict()
        update_settings(
            webpack_loader_settings=self.webpack_loader_settings,
            celerybeat_schedule_settings=self.celerybeat_schedule_settings,
            figures_env_tokens=figures_env_tokens,
        )

        self.validate_webpack_loader_settings()

        if run_celery:
            self.validate_celerybeat_schedule_settings()
        else:
            assert self.celery_task_name not in self.celerybeat_schedule_settings

        assert figures_settings.env_tokens == figures_env_tokens
