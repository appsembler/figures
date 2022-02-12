"""Tests figures.apps module

"""

from __future__ import absolute_import
import mock
import pytest


class ProdSettingsType(object):
    PRODUCTION = u'production'


@pytest.mark.parametrize('klass, expected_val', [
    (ProdSettingsType, ProdSettingsType.PRODUCTION),
    ])
def test_production_settings_name(klass, expected_val):
    key = 'openedx.core.djangoapps.plugins.constants'
    module = mock.Mock()
    setattr(module, 'SettingsType', klass)
    with mock.patch.dict('sys.modules', {key: module}):
        from figures.apps import production_settings_name
        name = production_settings_name()
        assert name == expected_val


def test_figures_config_name():
    from figures.apps import FiguresConfig
    assert FiguresConfig.name == 'figures'
    assert FiguresConfig.verbose_name == 'Figures'
