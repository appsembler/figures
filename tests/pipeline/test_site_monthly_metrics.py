"""Test figures.pipeline.site_monthly_metrics module

This is initial test coverage

"""
from __future__ import absolute_import
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils.timezone import utc
from freezegun import freeze_time
import pytest

from figures.compat import RELEASE_LINE, StudentModule
from figures.models import SiteMonthlyMetrics
from figures.pipeline.site_monthly_metrics import fill_month, fill_last_month

from tests.factories import (
    SiteFactory,
    StudentModuleFactory,
)
from six.moves import range


@pytest.fixture
@pytest.mark.django_db
def smm_test_data(db):
    """
    Minimal test data for very simple test case
    """
    site = SiteFactory()
    mock_today = datetime(year=2020, month=2, day=1, tzinfo=utc)
    last_month = mock_today - relativedelta(months=1)
    month_before = last_month - relativedelta(months=1)
    month_before_sm = [StudentModuleFactory(created=month_before,
                                            modified=month_before)]
    last_month_sm = [StudentModuleFactory(created=last_month,
                                          modified=last_month) for i in range(2)]
    return dict(site=site,
                mock_today=mock_today,
                last_month=last_month,
                month_before=month_before,
                last_month_sm=last_month_sm,
                month_before_sm=month_before_sm)


def test_fill_month_with_sm_wo_overwrite(monkeypatch, smm_test_data):
    """
    """
    assert SiteMonthlyMetrics.objects.count() == 0
    mock_today = smm_test_data['mock_today']
    freezer = freeze_time(mock_today)
    freezer.start()

    site = smm_test_data['site']

    def mock_get_student_modules_for_site(site):
        assert site == site
        return StudentModule.objects.all()

    monkeypatch.setattr('figures.pipeline.site_monthly_metrics.get_student_modules_for_site',
                        mock_get_student_modules_for_site)

    obj, created = fill_month(site=site,
                              month_for=smm_test_data['month_before'],
                              student_modules=StudentModule.objects.all())
    freezer.stop()

    assert obj and created
    assert obj.active_user_count == len(smm_test_data['month_before_sm'])
    assert obj.site == site
    assert obj.month_for == smm_test_data['month_before'].date()


@pytest.mark.skipif(RELEASE_LINE=='ginkgo',
                    reason='Freezegun breaks the StudentModule query')
def test_fill_last_month_wo_overwrite(monkeypatch, smm_test_data):
    """
    This test breaks when run in the Ginkgo environment. The problem is that
    after `freezer.start()`, StudentModule queries on `modified` fields return
    empty results when there are data for the modified fields set for the filter
    values. See tests/test_ginkgo.py
    """
    assert SiteMonthlyMetrics.objects.count() == 0
    mock_today = smm_test_data['mock_today']
    freezer = freeze_time(mock_today)
    year_check = smm_test_data['last_month_sm'][0].modified.year
    assert StudentModule.objects.filter(modified__year=year_check), \
        'before freezegun start'
    freezer.start()
    assert StudentModule.objects.filter(modified__year=year_check), \
        'after freezegun start'

    site = smm_test_data['site']

    def mock_get_student_modules_for_site(site):
        assert site == site
        return StudentModule.objects.all()

    monkeypatch.setattr('figures.pipeline.site_monthly_metrics.get_student_modules_for_site',
                        mock_get_student_modules_for_site)

    obj, created = fill_last_month(site=site)
    freezer.stop()

    assert obj and created
    assert obj.active_user_count == len(smm_test_data['last_month_sm'])
    assert obj.site == site
    assert obj.month_for == smm_test_data['last_month'].date()
