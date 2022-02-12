"""
Provides application configuration for Figures.

As well as default values for running Figures along with functions to
add entries to the Django conf settings needed to run Figures.
"""

from __future__ import absolute_import
from django.apps import AppConfig

from openedx.core.djangoapps.plugins.constants import (
    ProjectType, SettingsType, PluginURLs, PluginSettings
)


def production_settings_name():
    """
    Helper for Hawthorn and Ironwood+ compatibility.

    This helper will explicitly break if something have changed in `SettingsType`.
    """
    return getattr(SettingsType, 'PRODUCTION')


class FiguresConfig(AppConfig):
    """
    Provides application configuration for Figures.
    """

    name = 'figures'
    verbose_name = 'Figures'

    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: u'figures',
                PluginURLs.REGEX: u'^figures/',
            }
        },

        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                production_settings_name(): {
                    PluginSettings.RELATIVE_PATH: u'settings.lms_production',
                },
            }
        },
    }
