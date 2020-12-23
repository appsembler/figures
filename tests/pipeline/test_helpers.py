"""Test Figures pipeline.helpers module

This module tests the helper code in `figures.pipeline.helpers`. The code in
that module is intended specifically to run in Figures pipeline without
consideration of running elsewhere, such as Figures API calls

# Engineering note on testing 'pipeline_date_for_rule'

We test using the current datetime instead of mockig a fixed datetime to
simulate 'now' primarily because timezone handling is tricky and we want to
mask a bug if the 'utcnow' mocking doesn't handle it correctly
"""

from datetime import datetime, date, timedelta
import pytest

from django.utils.timezone import utc
from figures.pipeline.helpers import (DateForCannotBeFutureError,
                                      pipeline_date_for_rule)
from figures.helpers import as_date


def test_pipeline_date_for_rule_get_yesterday_with_none():
    """Ensure function under test returns yesterday as a datetime.date instance
    """
    now = datetime.utcnow().replace(tzinfo=utc)
    date_for = pipeline_date_for_rule(None)
    assert isinstance(date_for, date)
    assert date_for == now.date() - timedelta(days=1)


def run_pipeline_date_for_rule_asserts(arg_datetime, expected_date):
    """Validate function works with different parameter types
    """
    assert pipeline_date_for_rule(arg_datetime) == expected_date
    # test as date
    assert pipeline_date_for_rule(arg_datetime.date()) == expected_date
    # test as string rep of datetime
    assert pipeline_date_for_rule(str(arg_datetime)) == expected_date
    # test as string rep of date
    assert pipeline_date_for_rule(str(arg_datetime.date())) == expected_date


@pytest.mark.parametrize('day_from_now', [-1, 0])
def test_pipeline_date_for_rule_get_yesterday(day_from_now):
    """Ensure function under test returns yesterday as a datetime.date instance
    """
    now = datetime.utcnow().replace(tzinfo=utc)
    arg_datetime = now + timedelta(days=day_from_now)
    expected_date = (now - timedelta(days=1)).date()
    run_pipeline_date_for_rule_asserts(arg_datetime, expected_date)


@pytest.mark.parametrize('days_in_past', [1, 2, 3, 10, 999])
def test_pipeline_date_for_rule_get_date_in_past(days_in_past):
    """Ensure function  under test returns a date instance of the arg date
    """
    arg_datetime = datetime.utcnow().replace(tzinfo=utc) - timedelta(
        days=days_in_past)
    expected_date = as_date(arg_datetime)
    run_pipeline_date_for_rule_asserts(arg_datetime, expected_date)


@pytest.mark.parametrize('days_in_future', [1, 2, 10, 999])
def test_pipeline_data_for_rule_raises_future_exception(days_in_future):
    """Ensure function under test raises DateForCannotBeFutureError for future
    dates
    """
    arg_date = datetime.utcnow().replace(tzinfo=utc) + timedelta(
        days=days_in_future)
    with pytest.raises(DateForCannotBeFutureError):
        pipeline_date_for_rule(arg_date)
