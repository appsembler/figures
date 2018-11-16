'''This module provides baseline logging for the Figures pipeline

Initial focus is on tracking exceptions for Course

'''

import logging
import json

from django.core.serializers.json import DjangoJSONEncoder

from figures.models import PipelineError
from figures import settings

logger = logging.getLogger(__name__)


def log_error(error_data, error_type=None, **kwargs):
    logger.error(json.dumps(
        error_data,
        sort_keys=True,
        indent=1,
        cls=DjangoJSONEncoder
    ))

    if settings.log_pipeline_errors_to_db() or kwargs.get('log_pipeline_errors_to_db', False):
        data = dict(
            error_data=error_data,
            error_type=error_type or PipelineError.UNSPECIFIED_DATA,
            )
        if 'user' in kwargs:
            data.update(user=kwargs['user'])
        if 'course_id' in kwargs:
            data.update(course_id=str(kwargs['course_id']))
        PipelineError.objects.create(**data)
