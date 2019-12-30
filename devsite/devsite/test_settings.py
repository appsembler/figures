"""
Settings file to run automated tests

"""

from __future__ import absolute_import, unicode_literals

import os
from os.path import abspath, dirname, join
import sys

from figures.settings.lms_production import (
    update_celerybeat_schedule,
    update_webpack_loader,
)


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


OPENEDX_RELEASE = os.environ.get('OPENEDX_RELEASE', 'HAWTHORN').upper()

if OPENEDX_RELEASE == 'GINKGO':
    MOCKS_DIR = 'ginkgo'
else:
    MOCKS_DIR = 'hawthorn'

sys.path.append(root('mocks', MOCKS_DIR))


# Set the default Site (django.contrib.sites.models.Site)
SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'rest_framework',
    'django_countries',
    'django_filters',
    'devsite',
    'webpack_loader',
    'figures',

    # edx-platform apps. Mocks are used by default
    # See: edx-figures/tests/mocks/
    # Also note the paths set in edx-figures/pytest.ini
    'courseware',
    'openedx.core.djangoapps.content.course_overviews',
    'openedx.core.djangoapps.course_groups',
    'student',
    'organizations',
]

if OPENEDX_RELEASE == 'GINKGO':
    INSTALLED_APPS.append('certificates')
else:
    INSTALLED_APPS.append('lms.djangoapps.certificates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join('devsite', 'devsite', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


LOCALE_PATHS = [
    root('figures', 'conf', 'locale'),
]

ROOT_URLCONF = 'figures.urls'

SECRET_KEY = 'insecure-secret-key'

USE_TZ = True
TIME_ZONE = 'UTC'

# https://wsvincent.com/django-rest-framework-serializers-viewsets-routers/

# For initial testing, later we want to enforce authorization
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

# Webpack loader is required to load Figure's front-end
WEBPACK_LOADER = {}

CELERYBEAT_SCHEDULE = {}
FEATURES = {}

# The LMS defines ``ENV_TOKENS`` to load settings declared in `lms.env.json`
# We have an empty dict here to replicate behavior in the LMS
ENV_TOKENS = {}

update_webpack_loader(WEBPACK_LOADER, ENV_TOKENS)
update_celerybeat_schedule(CELERYBEAT_SCHEDULE, ENV_TOKENS)
