'''
This module provides default values for running edx-figures.

'''
import os

from django.conf import settings as django_settings

# Specity the 'edx_figures' package directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Define our webpack asset bundling constants
WEBPACK_BUNDLE_DIR_NAME = 'edx_figures_bundles/'
WEBPACK_STATS_FILE = os.path.abspath(
    os.path.join(APP_DIR, '../frontend/webpack-stats.json'))

# This will raise an AttributeError if WEBPACK_LOADER is not defined in settings
# We'll just let it fail
django_settings.WEBPACK_LOADER.update(EDX_FIGURES_APP={
    'BUNDLE_DIR_NAME': WEBPACK_BUNDLE_DIR_NAME,
    'STATS_FILE': WEBPACK_STATS_FILE
    })

# Add edx-figures settings here. These are for edx-figures operational defaults
EDX_FIGURES = {
    'APP_DIR': APP_DIR,
}
