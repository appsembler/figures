"""
Django settings for the Figures devsite development server

"""

from __future__ import absolute_import, unicode_literals

import os
import sys


DEVSITE_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT_DIR = os.path.dirname(DEVSITE_BASE_DIR)

# SECURITY WARNING: Use a real key when running in the cloud and keep it secret
SECRET_KEY = 'insecure-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
USE_TZ = True
TIME_ZONE = 'UTC'
ALLOWED_HOSTS = []

# Needed for Python to find the mock edx-platform modules
sys.path.append(
    os.path.normpath(os.path.join(PROJECT_ROOT_DIR, 'tests/mocks'))
    )

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'django_countries',
    'django_filters',
    # 'rest_framework.authtoken',
    'webpack_loader',
    'devsite',
    'figures',

    # edx-platform apps. Mocks are used by default
    # See: figures/tests/mocks/
    # Also note the paths set in edx-figures/pytest.ini
    'courseware',
    'openedx.core.djangoapps.content.course_overviews',
    'student',
    'certificates',
)

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


# It expects them from the project's settings (django.conf.settings)
WEBPACK_LOADER = {}
CELERYBEAT_SCHEDULE = {}

# Declare values we need from server vars (e.g. lms.env.json)
ENV_TOKENS = {}

# Enable Figures if it is included
# This should be the same code as used in the LMS settings
if 'figures' in INSTALLED_APPS:
    import figures
    figures.update_settings(
        WEBPACK_LOADER,
        CELERYBEAT_SCHEDULE,
        ENV_TOKENS.get('FIGURES', {}))
