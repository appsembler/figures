"""
Settings file to run automated tests

"""

from __future__ import absolute_import, unicode_literals

from os.path import abspath, dirname, join

from figures.settings.lms_production import (
    update_celerybeat_schedule,
    update_webpack_loader,
)


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


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


# certificates app

# edx-platform uses the app config
# 'lms.djangoapps.certificates.apps.CertificatesConfig'
# Our mock uses the package path
# TO emulate pre-hawthorn
#  INSTALLED_APPS += ('certificates')

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

# It expects them from the project's settings (django.conf.settings)
WEBPACK_LOADER = {}
CELERYBEAT_SCHEDULE = {}

FEATURES = {}

# TODO: Make conditional
INSTALLED_APPS.append('appsembler_reporting')
FEATURES.update({
    'FIGURES_INCLUDE_SUPERUSER_FIELD_IN_USER_REPORT': True,
})


# Declare values we need from server vars (e.g. lms.env.json)
ENV_TOKENS = {
    'FIGURES': {
        'WEBPACK_STATS_FILE': '../tests/test-webpack-stats.json',
    }
}


ENV_TOKENS['APPSEMBLER_REPORTING'] = {
    'DEFAULT_REPORT_ENCODING': 'utf-8',
    'REPORT_ROW_BUILDERS': {
        'learners': 'appsembler_reporting.reportgen.builders.DemographicReportRowBuilder',
        'grades': 'appsembler_reporting.reportgen.builders.GradeReportRowBuilder',
        'course-metrics': 'appsembler_reporting.reportgen.builders.CourseMetricsReportRowBuilder',
    },
    'INCLUDE_SUPERUSER_FIELD_IN_USER_REPORT' : False,
}

GRADES_DOWNLOAD = {
    "BUCKET": "staging-tahoe-grade-bucket",
    "ROOT_PATH": "grades",
    "STORAGE_CLASS": "storages.backends.s3boto.S3BotoStorage",
    "STORAGE_KWARGS": {},
    "STORAGE_TYPE": "S3"
}

AWS_ACCESS_KEY_ID = 'blah-blah-blah'
AWS_SECRET_ACCESS_KEY = 'blah-blah-blah-123'

update_webpack_loader(WEBPACK_LOADER, ENV_TOKENS)
update_celerybeat_schedule(CELERYBEAT_SCHEDULE, ENV_TOKENS)
