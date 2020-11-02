"""Site Celery setup
"""

from __future__ import absolute_import, unicode_literals
from __future__ import print_function
import os
from celery import Celery
from django.conf import settings


CELERY_CHECK_MSG_PREFIX = 'figures-devsite-celery-check'


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devsite.settings')

app = Celery('devsite')

# For Celery 4.0+
#
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# See: https://docs.celeryproject.org/en/4.0/whatsnew-4.0.html
# `app.config_from_object('django.conf:settings', namespace='CELERY')`

app.config_from_object('django.conf:settings')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)


@app.task(bind=True)
def debug_task(self):
    print(('Request: {0!r}'.format(self.request)))


@app.task(bind=True)
def celery_check(self, msg):
    """Basic system check to check Celery results in devsite

    Returns a value so that we can test Celery results backend configuration
    """
    print(('Called devsite.celery.celery.check with message "{}"'.format(msg)))
    return '{prefix}:{msg}'.format(prefix=CELERY_CHECK_MSG_PREFIX, msg=msg)
