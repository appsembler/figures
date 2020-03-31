
from datetime import datetime
from freezegun import freeze_time

from courseware.models import StudentModule

from figures.sites import (
    get_student_modules_for_site,
    get_student_modules_for_course_in_site,
)
from figures.mau import (
    get_mau_from_student_modules,
    get_mau_from_site_course,
    store_mau_metrics,
)


def test_get_mau_from_site_course(sm_test_data):
    """Basic test for coverage with simple check
    TODO: Improve by adding more students to the StudentModule instances for
    the first course constructed in the `sm_test_data` fixture data set.
    """
    year_for = sm_test_data['year_for']
    month_for = sm_test_data['month_for']
    site = sm_test_data['site']

    # Get first course, check student modules for that
    course_overview = sm_test_data['course_overviews'][0]
    users = get_mau_from_site_course(site=site,
                                     course_id=str(course_overview.id),
                                     year=year_for,
                                     month=month_for)
    course_sm = StudentModule.objects.filter(course_id=course_overview.id)
    sm_check = course_sm.values_list('student__id', flat=True).distinct()
    assert set(users) == set(sm_check)


def test_get_mau_from_sm_for_site(sm_test_data):
    year_for = sm_test_data['year_for']
    month_for = sm_test_data['month_for']
    sm = get_student_modules_for_site(sm_test_data['site'])
    users = get_mau_from_student_modules(student_modules=sm,
                                         year=year_for,
                                         month=month_for)

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
        # TODO: Fix, rudimentary check, improve
        assert expected_mau
