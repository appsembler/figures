"""
Django settings for the Figures devsite development server

This settings file is intended for operation only in a development environment
"""

from __future__ import absolute_import, unicode_literals

import os
import sys

from figures.settings.lms_production import (
    update_celerybeat_schedule,
    update_webpack_loader,
)


DEVSITE_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT_DIR = os.path.dirname(DEVSITE_BASE_DIR)

# SECURITY WARNING: Use a real key when running in the cloud and keep it secret
SECRET_KEY = 'insecure-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
USE_TZ = True
TIME_ZONE = 'UTC'
ALLOWED_HOSTS = []

# Set the default Site (django.contrib.sites.models.Site)
SITE_ID = 1

# Adds the mock edx-platform modules to the Python module search path
sys.path.append(
    os.path.normpath(os.path.join(PROJECT_ROOT_DIR, 'mocks/hawthorn'))
    )

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'django_countries',
    'django_filters',
    # 'rest_framework.authtoken',
    'webpack_loader',
    'devsite',
    'figures',

    # Include mock edx-platform apps.
    # These are apps on which Figures has dependencies
    # See: <figures repo>/tests/mocks/
    # Also note the paths set in edx-figures/pytest.ini
    'courseware',
    'openedx.core.djangoapps.content.course_overviews',
    'openedx.core.djangoapps.course_groups',
    'student',
]

# certificates app

# edx-platform uses the app config
# 'lms.djangoapps.certificates.apps.CertificatesConfig'
# Our mock uses the package path
# TO emulate pre-hawthorn
#   INSTALLED_APPS += ('certificates')
INSTALLED_APPS.append('lms.djangoapps.certificates')


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'devsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join('devsite', 'devsite', 'templates'),
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

# Static content
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(DEVSITE_BASE_DIR, "staticfiles")

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

WSGI_APPLICATION = 'devsite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DEVSITE_BASE_DIR, 'figures-db.sqlite3'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

LOCALE_PATHS = [
   os.path.join(PROJECT_ROOT_DIR, 'figures', 'conf', 'locale')
]


LOGIN_REDIRECT_URL = '/'

# Open edX settings

COURSE_ID_PATTERN = r'(?P<course_id>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)'

# For initial testing. Later we want to enforce authorization
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}


#
# Declare empty dicts for settings required by Figures
#


# Webpack loader is required to load Figure's front-end
WEBPACK_LOADER = {}


# Blank dict declared so that the Figures settings dependencies
# Included here for completeness in having this settings file match behavior in
# the LMS settings
CELERYBEAT_SCHEDULE = {}
FEATURES = {}

FEATURES = {}

# The LMS defines ``ENV_TOKENS`` to load settings declared in `lms.env.json`
# We have an empty dict here to replicate behavior in the LMS
ENV_TOKENS = {}

update_webpack_loader(WEBPACK_LOADER, ENV_TOKENS)
update_celerybeat_schedule(CELERYBEAT_SCHEDULE, ENV_TOKENS)
