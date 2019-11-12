
from figures.sites import get_student_modules_for_site
from figures.mau import get_mau_from_student_modules


def test_get_mau_from_sm_for_site(sm_test_data):
    sm = get_student_modules_for_site(sm_test_data['site'])
    users = get_mau_from_student_modules(student_modules=sm,
                                         year=2019,
                                         month=10)

    sm_check = sm.values_list('student__id', flat=True).distinct()
    assert set(users) == set(sm_check)
