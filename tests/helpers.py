"""Helper methods for Figures testing
"""

from __future__ import absolute_import
import os
from dateutil.rrule import rrule, DAILY
from packaging import version

from organizations.models import Organization


# Ginkgo is the earliest supported platform
GINKGO = 'GINKGO'
HAWTHORN = 'HAWTHORN'


def platform_release():
    return os.environ.get('OPENEDX_RELEASE', HAWTHORN)


OPENEDX_RELEASE = platform_release()


class FakeException(Exception):
    """Exception used for testing
    """
    pass


def make_course_key_str(org, number, run='test-run'):
    """
    Helper method to create a string representation of a CourseKey
    """
    return 'course-v1:{}+{}+{}'.format(org, number, run)


def create_metrics_model_timeseries(factory, first_day, last_day):
    """
    Convenience method to create a set of time series factory objects
    """
    return [factory(date_for=dt)
            for dt in rrule(DAILY, dtstart=first_day, until=last_day)]


def organizations_support_sites():
    """
    This function returns True if organizations supports site-organization
    mapping, False otherwise.

    This is used to conditionally run tests
    """
    orgs_has_site = hasattr(Organization, 'sites')
    return orgs_has_site


def django_filters_pre_v1():
    """Returns `True` if the installed Django Filters package is before '1.0.0'
    """
    import django_filters
    return version.parse(django_filters.__version__) < version.parse('1.0.0')


def django_filters_pre_v2():
    """Returns `True` if the installed Django Filters package is before '1.0.0'
    """
    import django_filters
    return version.parse(django_filters.__version__) < version.parse('2.0.0')
