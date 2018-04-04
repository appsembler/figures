"""

JLB: Copied/adapted from edx-ace

These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.

tried loading lms.envs.common. tests seemed to hang

So being explicit
"""

from __future__ import absolute_import, unicode_literals

from os.path import abspath, dirname, join
from path import Path 

#from lms.envs.common import *


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)

#TEST_ROOT = Path("/edx/app/edxapp/edx-platform/test_root")

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
    'rest_framework',
    'django_filters',
    'devsite',
    'edx_figures',

    # edx-platform installed apps

    # Course data caching
    #'openedx.core.djangoapps.content.course_overviews',
    #'openedx.core.djangoapps.content.course_structures.apps.CourseStructuresConfig',
    #'openedx.core.djangoapps.content.block_structure.apps.BlockStructureConfig',
    #'lms.djangoapps.course_blocks',

    # Student Identity Verification
    #'lms.djangoapps.verify_student',
    #'commerce',
    #'student'

    # edx-platform installed apps or Mocks
    # For the mock modules, see edx-figures/tests/mocks
    'openedx.core.djangoapps.content.course_overviews',

)

LOCALE_PATHS = [
    root('edx_figures', 'conf', 'locale'),
]

ROOT_URLCONF = 'edx_figures.urls'

SECRET_KEY = 'insecure-secret-key'

# https://wsvincent.com/django-rest-framework-serializers-viewsets-routers/

# For initial testing, later we want to enforce authorization
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}


WEBPACK_LOADER = {}

from edx_figures.settings import EDX_FIGURES
