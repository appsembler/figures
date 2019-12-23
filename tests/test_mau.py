
from datetime import datetime
from freezegun import freeze_time

from figures.sites import (
    get_student_modules_for_site,
    get_student_modules_for_course_in_site,
)
from figures.mau import (
    get_mau_from_student_modules,
    store_mau_metrics,
)


def test_get_mau_from_sm_for_site(sm_test_data):
    sm = get_student_modules_for_site(sm_test_data['site'])
    users = get_mau_from_student_modules(student_modules=sm,
                                         year=2019,
                                         month=10)

    sm_check = sm.values_list('student__id', flat=True).distinct()
    assert set(users) == set(sm_check)


def test_store_mau_metrics(monkeypatch, sm_test_data):
    """
    Basic minimal test
    """
    mock_today = datetime(year=sm_test_data['year_for'],
                          month=sm_test_data['month_for'],
                          day=1)
    freezer = freeze_time(mock_today)
    freezer.start()
    site = sm_test_data['site']
    data = store_mau_metrics(site=site)
    freezer.stop()

    site_mau = data['smo'].mau
    assert site_mau == len(sm_test_data['student_modules'])
    assert data['smo'].year == mock_today.year
    assert data['smo'].month == mock_today.month
    assert len(data['cmos']) == len(sm_test_data['course_overviews'])
    for cmo in data['cmos']:
        assert cmo.year == mock_today.year
        assert cmo.month == mock_today.month
        expected_course_sm = get_student_modules_for_course_in_site(site=site,
                                                                    course_id=cmo.course_id)
        expected_mau = get_mau_from_student_modules(student_modules=expected_course_sm,
                                                    year=mock_today.year,
                                                    month=mock_today.month)
