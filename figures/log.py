"""Provides logging and instrumentation functionality for Figures

"""

from contextlib import contextmanager
import logging
import timeit


default_logger = logging.getLogger(__name__)


@contextmanager
def log_exec_time(description, logger=None):
    """Context handler to log execution time info for a block

    Parameters:
    description : The text to add to the log statement
    logger : The logger to receive the log statement

    If `logger' is not provided, then the default logger is used,

        `logging.getLogger(__name__)`

    Example:

    ```
    with log_exec_time('Collect grades for courses in site',logger=my_logger):
        do_grades_collection(site=my_site)
    ```
    """
    logger = logger if logger else default_logger
    start_time = timeit.default_timer()
    yield
    elapsed = timeit.default_timer() - start_time
    msg = '{}: {} s'.format(description, elapsed)

    logger.info(msg)
