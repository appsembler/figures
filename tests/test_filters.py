"""Tests Figures filter classes

Currently uses Django TestCase style classes instead of pytest style classes
so that we can use TestCase.assertQuerysetEqual


Test Debt
=========
Field parameters 'lookup_type' and 'lookup_expr'

We are not adequately testing 'lookup_exr', which is supported only in
Django Filter 1.0.0 and greater. Prior to Django Filters 1.0.0, 'lookup_type'
was used.

* Open edX Ginkgo uses Django Filter 0.11.0
* Open edX Hawthorn uses Django Filter 1.0.4
* Open edX Juniper uses Django Fitler 2.2.0

TODO: Create mock view that tests the filters

Doing this instead of directly calling the filter make sure that the execution
chain is called. One of the defects we find is that our tests currently don't
adequately tests for method signature differences for our custom filter methods.
We need to make sure that our custom methods are properly handled by the
different versions of "Django Filter", as different major relases are used by
different Open edX releases.
"""

from __future__ import absolute_import
from dateutil.parser import parse as dateutil_parse

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase

from figures.compat import CourseEnrollment, CourseOverview
from figures.filters import (
    CourseDailyMetricsFilter,
    CourseEnrollmentFilter,
    CourseOverviewFilter,
    EnrollmentMetricsFilter,
    SiteDailyMetricsFilter,
    CourseMauMetricsFilter,
    SiteMauMetricsFilter,
    SiteFilterSet,
    UserFilterSet,
)
from figures.models import (
    CourseDailyMetrics,
    SiteDailyMetrics,
    CourseMauMetrics,
    SiteMauMetrics,
    LearnerCourseGradeMetrics,
)

from tests.factories import (
    CourseDailyMetricsFactory,
    CourseEnrollmentFactory,
    CourseMauMetricsFactory,
    CourseOverviewFactory,
    LearnerCourseGradeMetricsFactory,
    SiteDailyMetricsFactory,
    SiteMauMetricsFactory,
    SiteFactory,
    UserFactory,
)
from tests.helpers import make_course_key_str, django_filters_pre_v1
import six
from six.moves import range

# Because we are testing filtering on CourseOverview fields, we want to set
# specific values to facilitate filtering
COURSE_DATA = [
    {'org': 'AlphaOrg', 'number': 'A001'},
    {'org': 'AlphaOrg', 'number': 'A002'},
    {'org': 'BravoOrg', 'number': 'B001'},
    {'org': 'BravoOrg', 'number': 'B002'},
]


def make_course(**kwargs):
    id = make_course_key_str(**kwargs)
    return CourseOverviewFactory(
        id=id, org=kwargs['org'], number=kwargs['number'])


USER_DATA = [
    {'id': 1, 'username': u'alpha', 'fullname': u'Alpha One'},
    {'id': 2, 'username': u'alpha02', 'fullname': u'Alpha Two'},
    {'id': 3, 'username': u'bravo', 'fullname': u'Bravo One'},
    {'id': 4, 'username': u'bravo02', 'fullname': u'Bravo Two'},
]


def make_user(**kwargs):
    return UserFactory(
        id=kwargs['id'], username=kwargs['username'], profile__name=kwargs['fullname'])


@pytest.mark.skipif(django_filters_pre_v1(),
                    reason='Django Filter backward compatibility not implemented')
@pytest.mark.django_db
class CourseEnrollmentFilterTest(TestCase):
    def setUp(self):
        self.course_enrollments = [CourseEnrollmentFactory() for i in range(1, 5)]

    def tearDown(self):
        pass

    def test_get_all_course_enrollments(self):
        f = CourseEnrollmentFilter(queryset=CourseEnrollment.objects.all())
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.course_enrollments],
            lambda o: o.id,
            ordered=False)

    def test_filter_course_id(self):
        '''
        Each default factory created course enrollment has a unique course id
        We use this to get the course id for the first CourseEnrollment object
        Then we filter results on this course id and compare to the results
        returned by the filter class
        '''
        course_id = CourseEnrollment.objects.all()[0].course_id
        expected_results = CourseEnrollment.objects.filter(course_id=course_id)
        assert expected_results.count() != len(self.course_enrollments)

        res = CourseEnrollmentFilter().filter_course_id(
            queryset=CourseEnrollment.objects.all(),
            name='course_id',
            value=str(course_id))
        self.assertQuerysetEqual(
            res,
            [o.id for o in expected_results],
            lambda o: o.id,
            ordered=False)


@pytest.mark.skipif(django_filters_pre_v1(),
                    reason='Django Filter backward compatibility not implemented')
@pytest.mark.django_db
class CourseOverviewFilterTest(TestCase):
    '''Tests the CourseOverviewFilter filter class
    '''

    def setUp(self):
        self.course_overviews = [make_course(**data) for data in COURSE_DATA]

    def tearDown(self):
        pass

    def test_get_all_courses(self):
        f = CourseOverviewFilter(queryset=CourseOverview.objects.all())
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.course_overviews],
            lambda o: o.id,
            ordered=False)

    def test_filter_exact_org(self):
        f = CourseOverviewFilter(
            queryset=CourseOverview.objects.filter(org='Alpha'))
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.course_overviews if o.org == 'Alpha'],
            lambda o: o.id,
            ordered=False)

    def test_filter_exact_number(self):
        f = CourseOverviewFilter(
            queryset=CourseOverview.objects.filter(number='A001'))
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.course_overviews if o.number == 'A001'],
            lambda o: o.id,
            ordered=False)

    def test_filter_number_contains(self):
        f = CourseOverviewFilter(
            queryset=CourseOverview.objects.filter(number__contains='001'))
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.course_overviews if '001' in o.number],
            lambda o: o.id,
            ordered=False)


@pytest.mark.skipif(django_filters_pre_v1(),
                    reason='Django Filter backward compatibility not implemented')
@pytest.mark.django_db
class CourseDailyMetricsFilterTest(TestCase):
    '''Tests the CourseDailyMetricsFilter filter class
    '''

    def setUp(self):
        self.models = [
            CourseDailyMetricsFactory() for i in range(1, 10)
        ]

    def tearDown(self):
        pass

    def test_get_by_date(self):
        the_date_str = '2018-01-02'
        the_date = dateutil_parse(the_date_str).date()

        f = CourseDailyMetricsFilter(
            queryset=CourseDailyMetrics.objects.filter(date_for=the_date))

        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.models if o.date_for == the_date],
            lambda o: o.id, ordered=False)

    @pytest.mark.skip("Not implemented yet")
    def test_get_by_course_id(self):
        pass


@pytest.mark.skipif(django_filters_pre_v1(),
                    reason='Django Filter backward compatibility not implemented')
@pytest.mark.django_db
class SiteDailyMetricsFilterTest(TestCase):
    '''Tests the SiteDailyMetricsFilter filter class
    '''

    def setUp(self):
        self.site_daily_metrics = [
            SiteDailyMetricsFactory() for i in range(1, 10)
        ]

    def tearDown(self):
        pass

    def test_get_by_date(self):
        the_date_str = '2018-01-02'
        the_date = dateutil_parse(the_date_str).date()

        f = SiteDailyMetricsFilter(
            queryset=SiteDailyMetrics.objects.filter(date_for=the_date))

        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.site_daily_metrics if o.date_for == the_date],
            lambda o: o.id, ordered=False)


@pytest.mark.skipif(django_filters_pre_v1(),
                    reason='Django Filter backward compatibility not implemented')
@pytest.mark.django_db
class CourseMauMetricsFilterTest(TestCase):
    '''Tests the CourseMauMetricsFilter filter class
    '''

    def setUp(self):
        self.models = [
            CourseMauMetricsFactory() for i in range(1, 10)
        ]

    def tearDown(self):
        pass

    def test_get_by_date(self):
        the_date_str = '2018-01-02'
        the_date = dateutil_parse(the_date_str).date()

        f = CourseMauMetricsFilter(
            queryset=CourseMauMetrics.objects.filter(date_for=the_date))

        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.models if o.date_for == the_date],
            lambda o: o.id, ordered=False)

    @pytest.mark.skip("Not implemented yet")
    def test_get_by_course_id(self):
        pass


@pytest.mark.skipif(django_filters_pre_v1(),
                    reason='Django Filter backward compatibility not implemented')
@pytest.mark.django_db
class SiteMauMetricsFilterTest(TestCase):
    '''Tests the SiteDailyMetricsFilter filter class
    '''

    def setUp(self):
        self.models = [
            SiteMauMetricsFactory() for i in range(1, 10)
        ]

    def tearDown(self):
        pass

    def test_get_by_date(self):
        the_date_str = '2018-01-02'
        the_date = dateutil_parse(the_date_str).date()

        f = SiteMauMetricsFilter(
            queryset=SiteMauMetrics.objects.filter(date_for=the_date))

        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.models if o.date_for == the_date],
            lambda o: o.id, ordered=False)


@pytest.mark.skipif(django_filters_pre_v1(),
                    reason='Django Filter backward compatibility not implemented')
@pytest.mark.django_db
class EnrollmentMetricsFilterTest(TestCase):
    """
    Initially adding coverage where view tests are not covering
    """

    def setUp(self):
        self.site = SiteFactory()

        self.not_complete = LearnerCourseGradeMetricsFactory(site=self.site,
                                                             sections_worked=1,
                                                             sections_possible=2)
        self.complete = LearnerCourseGradeMetricsFactory(site=self.site,
                                                         sections_worked=2,
                                                         sections_possible=2)
        self.site_qs = LearnerCourseGradeMetrics.objects.filter(site=self.site)
        self.filter = EnrollmentMetricsFilter(queryset=self.site_qs)

    def test_filter_only_completed(self):
        qs = self.filter.filter_only_completed(queryset=self.site_qs,
                                               name='only_completed',
                                               value=True)
        assert qs.count() == 1 and qs[0] == self.complete

    def test_filter_only_completed_no_value(self):
        """Test that the method returns the queryset passed in
        """
        qs = self.filter.filter_only_completed(queryset=self.site_qs,
                                               name='only_completed',
                                               value=False)
        assert qs == self.site_qs

    def test_filter_exclude_completed(self):
        qs = self.filter.filter_exclude_completed(queryset=self.site_qs,
                                                  name='exclude_completed',
                                                  value=True)
        assert qs.count() == 1 and qs[0] == self.not_complete

    def test_filter_only_excluded_no_value(self):
        """Test that the method returns the queryset passed in
        """
        qs = self.filter.filter_exclude_completed(queryset=self.site_qs,
                                                  name='exclude_completed',
                                                  value=False)
        assert qs == self.site_qs


@pytest.mark.skipif(django_filters_pre_v1(),
                    reason='Django Filter backward compatibility not implemented')
@pytest.mark.django_db
class SiteFilterSetTest(TestCase):
    """Provides minimal testing for each of the individual filter terms
    * No filter - All sites should be returned
    * domain filter - filters case insensitive contains
    * name filter - filters case insensitive contains

    Did not add test for filtering on mulitple filter terms
    """

    def setUp(self):
        """There should be an existing site with domain and name of u'example.com'
        """
        assert Site.objects.count() == 1
        self.sites = [
            Site.objects.first(),
            SiteFactory(domain=u'alpha.test.site', name=u'Alpha'),
            SiteFactory(domain=u'bravo.test.site', name=u'Bravo Organization'),
        ]

    def test_filter_none(self):

        f = SiteFilterSet(
            queryset=Site.objects.filter())
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.sites],
            lambda o: o.id,
            ordered=False)

    def test_filter_domain_alpha(self):
        filter_term = 'ALpHA'
        f = SiteFilterSet(
            queryset=Site.objects.filter(domain__icontains=filter_term))
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.sites if filter_term.lower() in o.domain.lower()],
            lambda o: o.id, ordered=False)

    def test_filter_name_bravo(self):
        filter_term = 'BRaVO'
        f = SiteFilterSet(
            queryset=Site.objects.filter(name__icontains=filter_term))
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.sites if filter_term.lower() in o.name.lower()],
            lambda o: o.id, ordered=False)


@pytest.mark.skipif(django_filters_pre_v1(),
                    reason='Django Filter backward compatibility not implemented')
@pytest.mark.django_db
class UserFilterSetTest(TestCase):
    '''Tests the UserFilterSet filter class
    '''

    def setUp(self):
        self.User = get_user_model()
        self.users = [make_user(**data) for data in USER_DATA]
        self.course_overview = CourseOverviewFactory()
        self.course_enrollments = [
            CourseEnrollmentFactory(course_id=self.course_overview.id,
                                    user=self.users[i]) for i in range(2)]

    def tearDown(self):
        pass

    def test_get_all_users(self):
        f = UserFilterSet(queryset=self.User.objects.all())
        self.assertQuerysetEqual(
            f.qs,
            [o.id for o in self.users],
            lambda o: o.id,
            ordered=False)

    def test_filter_user_ids(self):
        res = UserFilterSet().filter_user_ids(
            queryset=self.User.objects.all(),
            name='user_ids',
            value='{},{}'.format(self.users[0].id, self.users[1].id))

        self.assertQuerysetEqual(
            res,
            [o.id for o in self.users[:2]],
            lambda o: o.id, ordered=False)

    def test_filter_enrolled_in_course_id(self):
        res = UserFilterSet().filter_enrolled_in_course_id(
            queryset=self.User.objects.all(),
            name='course_id',
            value=six.text_type(self.course_overview.id))

        self.assertQuerysetEqual(
            res,
            [o.id for o in self.users[:2]],
            lambda o: o.id, ordered=False)
