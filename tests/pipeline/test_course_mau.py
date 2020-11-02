"""
Tests Course Monthly Active Users (MAUs)

* Test pipeline loading MAU data
"""

from __future__ import absolute_import
from datetime import datetime, date
import pytest
from mock import Mock

from factory import fuzzy

from figures.pipeline.mau_pipeline import (
    get_all_mau_for_site_course,
    calculate_course_mau,
    save_course_mau,
    collect_course_mau,
)

from tests.factories import (
    SiteFactory,
    CourseOverviewFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
    StudentModuleFactory,
)

from tests.helpers import organizations_support_sites
from six.moves import range

if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory


def create_student_module_recs(course_id):
    """
    Create StudentModule records for our test data
    We create records within the test month and before and after our test month

    Improve this by passing the year and month for which we want to check
    record inclusion and deriving dates outside of our month range for the
    StudentModule records we want to exclude
    """
    # Create SM in our month
    year_for = 2020
    month_for = 1
    start_dt = datetime(year_for, month_for, 1, tzinfo=fuzzy.compat.UTC)
    end_dt = datetime(year_for, month_for, 31, tzinfo=fuzzy.compat.UTC)
    date_gen = fuzzy.FuzzyDateTime(start_dt=start_dt, end_dt=end_dt)

    in_range = [StudentModuleFactory(created=start_dt,
                                     modified=date_gen.evaluate(2, None, False),
                                     course_id=course_id)
                for i in range(3)]
    # Create a rec before
    before_date = datetime(2019, 12, 31, tzinfo=fuzzy.compat.UTC)
    # Create a rec after
    after_date = datetime(2020, 2, 1, tzinfo=fuzzy.compat.UTC)
    out_range = [
        StudentModuleFactory(created=before_date,
                             modified=before_date,
                             course_id=course_id),
        StudentModuleFactory(created=after_date,
                             modified=after_date,
                             course_id=course_id)
    ]
    return dict(
        year_for=year_for,
        month_for=month_for,
        in_range=in_range,
        out_range=out_range,
    )


@pytest.fixture
def simple_mau_test_data(settings):
    """
    Pytest fixture to create the base test data we need for the MAU tests here

    We set up single site vs multisite mode in this fixture based on which
    edx-organizations package is declared in the pip requirements file used to
    run the tests:

    Community:
    edx-organizations==0.4.10

    Tahoe:
    git+https://github.com/appsembler/edx-organizations.git@0.4.12-appsembler4
    """
    our_site = SiteFactory()
    our_org = OrganizationFactory()
    our_course = CourseOverviewFactory()
    our_other_course = CourseOverviewFactory()
    other_site = SiteFactory()
    other_site_course = CourseOverviewFactory()
    our_course_data = create_student_module_recs(our_course.id)
    our_other_course_sm = [StudentModuleFactory(course_id=our_other_course.id)
                           for i in range(10)]
    month_for = date(year=our_course_data['year_for'],
                     month=our_course_data['month_for'],
                     day=1)
    expected_mau_ids = set([rec.student.id for rec in our_course_data['in_range']])

    test_data = dict(
        month_for=month_for,
        expected_mau_ids=expected_mau_ids,
        our_site=our_site,
        our_course=our_course,
        our_course_data=our_course_data,
        our_other_course=our_other_course,
        our_other_course_sm=our_other_course_sm,
        other_site=other_site,
        other_site_course=other_site_course,
    )

    if organizations_support_sites():
        settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        our_org = OrganizationFactory(sites=[our_site])
        for user in set([obj.student for obj in our_course_data['in_range']]):
            UserOrganizationMappingFactory(user=user, organization=our_org)
        for course_id in set([obj.course_id for obj in our_course_data['in_range']]):
            OrganizationCourseFactory(organization=our_org,
                                      course_id=str(course_id))
    return test_data


@pytest.mark.django_db
def test_course_mau_etl(simple_mau_test_data):
    """
    Integration test for the functions in this mod
    Test that the pipeline loads data for a simple case
    """
    our_site = simple_mau_test_data['our_site']
    our_course = simple_mau_test_data['our_course']
    month_for = simple_mau_test_data['month_for']
    expected_mau_ids = simple_mau_test_data['expected_mau_ids']
    obj, created = collect_course_mau(site=our_site,
                                      courselike=our_course.id,
                                      month_for=month_for)
    assert obj
    assert created
    assert obj.mau == len(expected_mau_ids)


@pytest.mark.django_db
class TestExtractMauData(object):
    """
    Test retrieving StudentModule records from edx-platform
    """

    def test_simple_case(self, simple_mau_test_data):
        """
        Tests `get_all_mau_for_site_course` with the `simple_mau_test_data` fixture
        """
        our_site = simple_mau_test_data['our_site']
        our_course = simple_mau_test_data['our_course']
        month_for = simple_mau_test_data['month_for']
        expected_mau_ids = simple_mau_test_data['expected_mau_ids']

        mau_ids = get_all_mau_for_site_course(site=our_site,
                                              courselike=our_course.id,
                                              month_for=month_for)
        assert set(mau_ids.all()) == expected_mau_ids


@pytest.mark.django_db
class TestTransformMauData(object):
    """
    Test getting MAU count. This is the 'transform' step in ETL
    """
    def test_simple_case(self, simple_mau_test_data):
        mau_ids = Mock()
        mau_ids.count = Mock(return_value=42)
        mau_count = calculate_course_mau(mau_ids)
        assert mau_count == mau_ids.count()


@pytest.mark.django_db
class TestLoadMauData(object):
    """
    Test retrieving StudentModule records from edx-platform
    """
    def test_simple_case(self, ):
        site = SiteFactory()
        month_for = datetime(2019, 10, 29)
        course = CourseOverviewFactory()
        mau_data = dict(mau=5)
        obj, created = save_course_mau(site=site,
                                       courselike=course.id,
                                       month_for=month_for,
                                       mau_data=mau_data)
        assert obj
        assert created
        assert obj.mau == mau_data['mau']
