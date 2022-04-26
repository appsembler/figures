"""Tests MonthlyActiveEnrollment model

Initially just basic testing for coverage
"""
from __future__ import absolute_import
import six
from datetime import date
import pytest

from figures.models import MonthlyActiveEnrollment

from tests.factories import MonthlyActiveEnrollmentFactory
from tests.helpers import organizations_support_sites
from tests.conftest import make_site_data


@pytest.fixture
@pytest.mark.django_db
def mae_test_data(db, settings):
    """
    Because Figures `MonthlyActiveEnrollment` is decoupled from course data,
    we do not need to create enrollments
    """
    if organizations_support_sites():
        settings.FEATURES['FIGURES_IS_MULTISITE'] = True

    our_site_data = make_site_data(create_enrollments=False)
    other_site_data = make_site_data(create_enrollments=False)
    return dict(us=our_site_data, them=other_site_data)


@pytest.mark.parametrize('overwrite, expect_created', [
    (False, True),
    (True, True),
])
def test_add_mae_new_overwrite_option(mae_test_data,
                                      overwrite,
                                      expect_created):
    """
    Test 'overwrite' option when adding a monthly active enrollment
    """
    # Arrange
    us = mae_test_data['us']
    course_id = us['courses'][0].id
    user = us['users'][0]
    assert not MonthlyActiveEnrollment.objects.count()

    # Act
    obj, created = MonthlyActiveEnrollment.objects.add_mae(
        site_id=us['site'].id,
        course_id=course_id,
        user_id=user.id,
        overwrite=overwrite)

    # Assert
    assert obj
    assert created == expect_created
    assert MonthlyActiveEnrollment.objects.count() == 1


@pytest.mark.parametrize('overwrite, expect_created', [
    (False, False),
    (True, False),
])
def test_add_mae_existing_overwrite_option(mae_test_data,
                                           overwrite,
                                           expect_created):
    """
    Test 'overwrite' option when adding to an existing monthly active enrollment
    """

    # Arrange
    us = mae_test_data['us']
    course_id = us['courses'][0].id
    user = us['users'][0]
    date_for = date.today()
    month_for = date(year=date_for.year, month=date_for.month, day=1)
    mae = MonthlyActiveEnrollmentFactory(
        site=us['site'],
        course_id=six.text_type(course_id),
        user=user,
        month_for=month_for)

    assert MonthlyActiveEnrollment.objects.count() == 1

    # Act
    obj, created = MonthlyActiveEnrollment.objects.add_mae(
        site_id=us['site'].id,
        course_id=course_id,
        user_id=user.id,
        overwrite=overwrite)

    # Assert
    assert obj and obj.id and obj.id == mae.id
    assert created == expect_created
    assert MonthlyActiveEnrollment.objects.count() == 1


def test_add_mae_with_date_for(mae_test_data):
    """
    Test using the current date as 'date_for'
    """
    # Arrange
    us = mae_test_data['us']
    course_id = us['courses'][0].id
    user = us['users'][0]
    assert not MonthlyActiveEnrollment.objects.count()
    date_for = date.today()
    month_for = date(year=date_for.year, month=date_for.month, day=1)

    # Act
    obj, created = MonthlyActiveEnrollment.objects.add_mae(
        site_id=us['site'].id,
        course_id=course_id,
        user_id=user.id,
        date_for=date_for)

    # Assert
    assert obj and obj.id
    assert created
    assert MonthlyActiveEnrollment.objects.count() == 1
    assert obj.month_for == month_for
