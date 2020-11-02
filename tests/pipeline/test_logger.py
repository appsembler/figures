'''

NOTE: These tests need improvement

* Add testing to skip model via kwarg to override settings value

'''

from __future__ import absolute_import
import datetime
import mock
import pytest

from figures.pipeline import logger
from figures.models import PipelineError

from tests.factories import UserFactory


@pytest.mark.django_db
class TestPipelineLogging(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.error_data = dict(
            alpha_key='alpha-value',
            bravo_key='bravo-value',
            ts=datetime.datetime(2018, 2, 2, 6, 30)
            )
        self.user = UserFactory(username='bubba')

    def test_logging_to_logger(self):
        assert PipelineError.objects.count() == 0
        features = {'FIGURES_LOG_PIPELINE_ERRORS_TO_DB': False}
        with mock.patch('figures.helpers.settings.FEATURES', features):
            logger.log_error(self.error_data)
            assert PipelineError.objects.count() == 0

    def test_logging_to_model(self):
        assert PipelineError.objects.count() == 0
        logger.log_error(self.error_data)

    @pytest.mark.parametrize('dict_args', [
            {'username': 'bubba'},
            {'username': 'bubba', 'course_id': 'fake-course-id'}
        ])
    def test_logging_to_model_with_kwargs(self, dict_args):
        assert PipelineError.objects.count() == 0
        logger.log_error(self.error_data, **dict_args)
