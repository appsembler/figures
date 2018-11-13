"""
Settings file to run automated tests

"""

from __future__ import absolute_import, unicode_literals

from os.path import abspath, dirname, join
from path import Path 


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)

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


INSTALLED_APPS = (
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
    'student',
    'certificates',
    'organizations',
)

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

# It expects them from the project's settings (django.conf.settings)
WEBPACK_LOADER = {}
CELERYBEAT_SCHEDULE = {}

# Declare values we need from server vars (e.g. lms.env.json)
ENV_TOKENS = {
    'FIGURES': {
        'WEBPACK_STATS_FILE': '../tests/test-webpack-stats.json',
    }
}


# Enable Figures if it is included
# This should be the same code as used in the LMS settings
if 'figures' in INSTALLED_APPS:
    import figures
    figures.update_settings(
        WEBPACK_LOADER,
        CELERYBEAT_SCHEDULE,
        ENV_TOKENS.get('FIGURES', {}))

