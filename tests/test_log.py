"""Tests figures.log module
"""

import logging
import pytest

from figures.log import log_exec_time


logger = logging.getLogger(__name__)


def some_func():
    """Just a function we'll call to test the context manager
    """
    logger.info('Just some function')


@pytest.mark.django_db
class TestLogExecTime(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        pass

    def test_with_default_logger(self, caplog):
        """Our basic `log_exec_time` test
        """
        caplog.set_level(logging.INFO)
        my_message = 'my-message'
        with log_exec_time(my_message):
            some_func()
        last_log = caplog.records[-1]
        # Very basic check. We can improve on it by monkeypatching timit or just
        # checking the number and 's' for seconds at the end of the string
        # For now, we just want to check that our message gets into the log
        assert last_log.message.startswith(my_message)

    def test_with_param_logger(self, caplog):
        """Test when we provide a logger
        This is just a parameter check at this point. We're not checking that
        we have multiple logging buffers
        """
        caplog.set_level(logging.INFO)
        my_message = 'my-message'
        with log_exec_time(my_message, logger):
            some_func()
        last_log = caplog.records[-1]
        assert last_log.message.startswith(my_message)

    def test_log_level_warning(self, caplog):
        """Make sure we are not outputting the exec time on level > INFO
        """
        caplog.set_level(logging.WARNING)
        my_message = 'my-message'
        with log_exec_time(my_message):
            some_func()
        assert not caplog.records
