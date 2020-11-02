'''This module provides baseline logging for the Figures pipeline

Initial focus is on tracking exceptions for Course

'''

from __future__ import absolute_import
import logging
import json

from django.core.serializers.json import DjangoJSONEncoder

from figures.models import PipelineError
from figures import helpers as figure_helpers

default_logger = logging.getLogger(__name__)


def log_error_to_db(error_data, error_type, **kwargs):
    data = dict(
        error_data=error_data,
        error_type=error_type or PipelineError.UNSPECIFIED_DATA,
        )
    if 'user' in kwargs:
        data.update(user=kwargs['user'])
    if 'course_id' in kwargs:
        data.update(course_id=str(kwargs['course_id']))
    if 'site' in kwargs:
        data.update(site=kwargs['site'])
    PipelineError.objects.create(**data)


def log_error(error_data, error_type=None, **kwargs):
    kwargs.get('logger', default_logger).error(json.dumps(
        error_data,
        sort_keys=True,
        indent=1,
        cls=DjangoJSONEncoder))

    if figure_helpers.log_pipeline_errors_to_db() or kwargs.get('log_pipeline_errors_to_db', False):
        log_error_to_db(error_data, error_type, **kwargs)
