"""Tests Figures UserIndexView class

TODO: make reasonable endpoint


Front end expects data to be returned in the following form:

[
  {
    "username": "maxi",
    "country": "UY",
    "is_active": true,
    "year_of_birth": 1985,
    "level_of_education": "b",
    "gender": "m",
    "date_joined": "2018-05-06T14:01:58Z",
    "language_proficiencies": [],
    "courses": [
      {
        "course_name": "Something",
        "course_id": "A193+2016Q4+something",
      }
      ...
    ]
  },
  ...
]


"""

from __future__ import absolute_import
import mock
import pytest

from django.contrib.auth import get_user_model
from django.db.models import F

from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from figures.compat import CourseEnrollment
from figures.helpers import as_course_key
from figures.serializers import LearnerCourseDetailsSerializer
from figures.sites import get_course_enrollments_for_site
from figures.views import LearnerDetailsViewSet
import figures.settings

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
    SiteFactory,
    UserFactory,
    )

from tests.views.base import BaseViewTest
from tests.helpers import organizations_support_sites
from six.moves import range

if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory


USER_DATA = [
    {'id': 101, 'username': u'alpha', 'fullname': u'Alpha One',
     'is_active': True, 'country': 'CA'},
    {'id': 102, 'username': u'alpha02', 'fullname': u'Alpha Two', 'is_active': False, 'country': 'UK'},
    {'id': 103, 'username': u'bravo', 'fullname': u'Bravo One', 'is_active': True, 'country': 'US'},
    {'id': 104, 'username': u'bravo02', 'fullname': u'Bravo Two', 'is_active': True, 'country': 'UY'},
]

COURSE_DATA = [
    { 'id': u'course-v1:AlphaOrg+A001+RUN', 'name': u'Alpha Course 1', 'org': u'AlphaOrg', 'number': u'A001' },
    { 'id': u'course-v1:AlphaOrg+A002+RUN', 'name': u'Alpha Course 2', 'org': u'AlphaOrg', 'number': u'A002' },
    { 'id': u'course-v1:BravoOrg+A001+RUN', 'name': u'Bravo Course 1', 'org': u'BravoOrg', 'number': u'B001' },
    { 'id': u'course-v1:BravoOrg+B002+RUN', 'name': u'Bravo Course 2', 'org': u'BravoOrg', 'number': u'B002' },
]

def make_user(**kwargs):
    '''

    NOTE: Consider adding more fields. Refere to the serializer test for  the
    GeneralUserDataSerializer
    '''
    return UserFactory(
        id=kwargs['id'],
        username=kwargs['username'],
        profile__name=kwargs['fullname'],
        profile__country=kwargs['country'],
        is_active=kwargs['is_active'],
    )

def make_course(**kwargs):
    return CourseOverviewFactory(
        id=as_course_key(kwargs['id']),
        display_name=kwargs['name'],
        org=kwargs['org'],
        number=kwargs['number'],
    )

def make_course_enrollments_for_user(user, courses, **kwargs):
    '''
        creates course enrollments for every course in COURSE_DATA for the given user
    '''
    course_enrollments = []
    for course in courses:
        course_enrollments.append(
            CourseEnrollmentFactory(
                course_id=course.id,
                course_overview=course,
                user=user,
                )
            )
    return course_enrollments


def get_course_rec(course_id, course_list):
    recs = [rec for rec in course_list if rec['course_id'] == str(course_id)]
    assert len(recs) == 1
    return recs[0]


@pytest.mark.skipif(organizations_support_sites(),
                    reason='Organizations support sites')
@pytest.mark.django_db
class TestLearnerDetailsViewSetStandalone(BaseViewTest):
    '''Tests the UserIndexView view class
    '''

    request_path = 'api/users-detail/'
    view_class = LearnerDetailsViewSet
    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        super(TestLearnerDetailsViewSetStandalone, self).setup(db)
        self.course_overviews = [
            CourseOverviewFactory() for i in range(0,4)
        ]
        self.users = [UserFactory() for i in range(3)]

        self.enrollments = [
            CourseEnrollmentFactory(course=self.course_overviews[0],
                                    user=self.users[0]),
            CourseEnrollmentFactory(course=self.course_overviews[1],
                                    user=self.users[1]),
            CourseEnrollmentFactory(course=self.course_overviews[2],
                                    user=self.users[0]),
            CourseEnrollmentFactory(course=self.course_overviews[2],
                                    user=self.
                                    users[1]),
        ]

        self.expected_result_keys = [
            'id', 'username', 'name', 'email', 'country', 'is_active',
            'year_of_birth', 'level_of_education', 'gender', 'date_joined',
            'bio', 'courses', 'language_proficiencies', 'profile_image'
        ]

    def test_serializer(self):
        '''
        This test makes sure the serializer works with the test data provided
        in this Test class
        '''

        # Spot test with the first CourseEnrollment for the first user
        enrollments = get_course_enrollments_for_site(self.site)
        queryset = enrollments.filter(user=self.users[0])
        assert queryset
        serializer = LearnerCourseDetailsSerializer(queryset[0])
        # We're asserting that we can get the serializer `data` property without
        # error, not checking the contents of the data. That should be done in
        # the serializer specific tests (see tests/test_serializers.py).
        assert serializer.data

    def test_get_learner_details_retrieve(self):
        user = self.users[0]

        expected_enrollments = CourseEnrollment.objects.filter(user=user)
        request_path = self.request_path + '{}/'.format(user.id)
        request = APIRequestFactory().get(request_path)
        force_authenticate(request, user=self.staff_user)
        view = self.view_class.as_view({'get': 'retrieve'})
        response = view(request, pk=user.id)

        # ['id', 'username', 'name', 'email', 'country', 'is_active', 'year_of_birth', 'level_of_education', 'gender', 'date_joined', 'courses', 'language_proficiencies', 'profile_image']
        assert len(response.data['courses']) == expected_enrollments.count()
        assert set(response.data.keys()) == set(self.expected_result_keys)


    def test_get_learner_details_list(self):
        """Tests retrieving a list of users with abbreviated details

        The fields in each returned record are identified by
            `figures.serializers.UserIndexSerializer`

        """
        request = APIRequestFactory().get(self.request_path)
        force_authenticate(request, user=self.staff_user)
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)

        # Later, we'll elaborate on the tests. For now, some basic checks
        assert response.status_code == 200
        assert set(response.data.keys()) == set(
            ['count', 'next', 'previous', 'results'])

        results = response.data['results']
        assert len(results) == len(self.users) + len(self.callers)
        enrollments = get_course_enrollments_for_site(self.site)
        assert enrollments.count() == len(self.enrollments)

        for rec in results:
            assert set(rec.keys()) == set(self.expected_result_keys)
            # fail if we cannot find the user in the models
            user = get_user_model().objects.get(username=rec['username'])
            user_course_enrollments = enrollments.filter(user=user)
            # Check that each course enrollment is represented
            assert len(rec['courses']) == user_course_enrollments.count()
            for ce in user_course_enrollments:
                assert get_course_rec(ce.course_id, rec['courses'])


@pytest.mark.skipif(not organizations_support_sites(),
                    reason='Organizations support sites')
@pytest.mark.django_db
class TestLearnerDetailsViewSetMultisite(BaseViewTest):
    '''Tests the UserIndexView view class
    '''

    request_path = 'api/users-detail/'
    view_class = LearnerDetailsViewSet
    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        super(TestLearnerDetailsViewSetMultisite, self).setup(db)
        # TODO:REFACTOR:Make base 'multisite scaffolding' view test class to
        # set up the sites, orgs, and users. Put into tests/views/base.py
        settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        is_multisite = figures.helpers.is_multisite()
        assert is_multisite
        self.my_site_org = OrganizationFactory(sites=[self.site])
        self.other_site = SiteFactory(domain='other-site.test')
        self.other_site_org = OrganizationFactory(sites=[self.other_site])

        self.my_course_overviews = [
            CourseOverviewFactory() for i in range(0,4)
        ]

        for co in self.my_course_overviews:
            OrganizationCourseFactory(organization=self.my_site_org,
                                      course_id=str(co.id))

        # Set up users and enrollments for 'my site'
        self.my_site_users = [UserFactory() for i in range(3)]
        for user in self.my_site_users:
            UserOrganizationMappingFactory(user=user,
                                           organization=self.my_site_org)

        # Create a mix of enrollments:
        # one learner in one course, same for the other, then two learners in
        # the same course, and keep one course w/out learners
        self.my_enrollments = [
            CourseEnrollmentFactory(course=self.my_course_overviews[0],
                                    user=self.my_site_users[0]),
            CourseEnrollmentFactory(course=self.my_course_overviews[1],
                                    user=self.my_site_users[1]),
            CourseEnrollmentFactory(course=self.my_course_overviews[2],
                                    user=self.my_site_users[0]),
            CourseEnrollmentFactory(course=self.my_course_overviews[2],
                                    user=self.my_site_users[1]),
        ]

        self.caller = UserFactory()
        UserOrganizationMappingFactory(user=self.caller,
                                       organization=self.my_site_org,
                                       is_amc_admin=True)
        self.my_site_users.append(self.caller)
        # Set up other site's data
        self.other_site_enrollment =CourseEnrollmentFactory()
        OrganizationCourseFactory(organization=self.other_site_org,
                                  course_id=self.other_site_enrollment.course.id)
        UserOrganizationMappingFactory(user=self.other_site_enrollment.user,
                                       organization=self.other_site_org)

        self.expected_result_keys = [
            'id', 'username', 'name', 'email', 'country', 'is_active',
            'year_of_birth', 'level_of_education', 'gender', 'date_joined',
            'bio', 'courses', 'language_proficiencies', 'profile_image'
        ]

    def test_serializer(self):
        '''
        This test makes sure the serializer works with the test data provided
        in this Test class
        '''

        # Spot test with the first CourseEnrollment for the first user
        enrollments = get_course_enrollments_for_site(self.site)
        queryset = enrollments.filter(user=self.my_site_users[0])
        assert queryset
        serializer = LearnerCourseDetailsSerializer(queryset[0])
        # We're asserting that we can get the serializer `data` property without
        # error, not checking the contents of the data. That should be done in
        # the serializer specific tests (see tests/test_serializers.py).
        assert serializer.data

    def test_get_learner_details_retrieve(self):
        user = self.my_site_users[0]

        expected_enrollments = CourseEnrollment.objects.filter(user=user)
        request_path = self.request_path + '{}/'.format(user.id)
        request = APIRequestFactory().get(request_path)
        force_authenticate(request, user=self.caller)
        view = self.view_class.as_view({'get': 'retrieve'})
        response = view(request, pk=user.id)
        assert len(response.data['courses']) == expected_enrollments.count()

    def test_get_learner_details_list(self):
        """Tests retrieving a list of users with abbreviated details

        The fields in each returned record are identified by
            `figures.serializers.UserIndexSerializer`

        """

        request = APIRequestFactory().get(self.request_path)
        force_authenticate(request, user=self.caller)
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)

        # Later, we'll elaborate on the tests. For now, some basic checks
        assert response.status_code == 200
        assert set(response.data.keys()) == set(
            ['count', 'next', 'previous', 'results'])

        results = response.data['results']
        assert len(results) == len(self.my_site_users)
        enrollments = get_course_enrollments_for_site(self.site)
        assert enrollments.count() == len(self.my_enrollments)

        for rec in results:
            assert set(rec.keys()) == set(self.expected_result_keys)
            # fail if we cannot find the user in the models
            user = get_user_model().objects.get(username=rec['username'])
            user_course_enrollments = enrollments.filter(user=user)
            # Check that each course enrollment is represented
            assert len(rec['courses']) == user_course_enrollments.count()
            for ce in user_course_enrollments:
                assert get_course_rec(ce.course_id, rec['courses'])
