'''Tests Figures UserIndexView class

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


'''

import mock
import pytest

from django.contrib.auth import get_user_model
from django.db.models import F

from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from student.models import CourseEnrollment

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
    UserFactory,
    )

from tests.views.base import BaseViewTest
from tests.helpers import organizations_support_sites

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


@pytest.mark.django_db
class TestLearnerDetailsViewSet(BaseViewTest):
    '''Tests the UserIndexView view class
    '''

    request_path = 'api/users/detail/'
    view_class = LearnerDetailsViewSet
    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        super(TestLearnerDetailsViewSet, self).setup(db)
        self.users = [make_user(**data) for data in USER_DATA]
        self.usernames = [data['username'] for data in USER_DATA]
        self.course_overviews = [make_course(**data) for data in COURSE_DATA]
        self.course_enrollments = []
        for user in self.users:
            self.course_enrollments += make_course_enrollments_for_user(
                user, self.course_overviews)

        self.expected_result_keys = [
            'id', 'username', 'name', 'country', 'is_active', 'gender', 'email',
            'date_joined', 'year_of_birth', 'level_of_education', 'courses',
            'language_proficiencies', 'profile_image',
        ]

    def test_serializer(self):
        '''
        This test makes sure the serializer works with the test data provided
        in this Test class
        '''

        # Spot test with the first CourseEnrollment for the first user
        enrollments = get_course_enrollments_for_site(self.site)
        queryset = enrollments.filter(user=self.users[0])
        serializer = LearnerCourseDetailsSerializer(queryset[0])
        assert serializer.data

    def test_get_learner_details_retrieve(self):
        user = self.users[0]

        expected_enrollments = CourseEnrollment.objects.filter(user=user)
        request_path = self.request_path + '{}/'.format(user.id)
        request = APIRequestFactory().get(request_path)
        force_authenticate(request, user=self.staff_user)
        view = self.view_class.as_view({'get': 'retrieve'})
        response = view(request, pk=user.id)
        assert len(response.data['courses']) == expected_enrollments.count()
        # TODO: check each

    @pytest.mark.skipif(not organizations_support_sites(),
                        reason='Organizations support sites')
    def test_get_learner_details_list_multisite(self):
        """Tests retrieving a list of users with abbreviated details

        The fields in each returned record are identified by
            `figures.serializers.UserIndexSerializer`

        """
        env_tokens = {'FIGURES_IS_MULTISITE': True}
        with mock.patch('figures.helpers.settings.FEATURES', env_tokens):
            is_multisite = figures.helpers.is_multisite()
            assert is_multisite
            self.organization = OrganizationFactory(sites=[self.site])
            for co in self.course_overviews:
                OrganizationCourseFactory(organization=self.organization,
                                          course_id=str(co.id))

            for user in self.users:
                UserOrganizationMappingFactory(user=user,
                                               organization=self.organization)

            request = APIRequestFactory().get(self.request_path)
            force_authenticate(request, user=self.staff_user)
            view = self.view_class.as_view({'get': 'list'})
            response = view(request)

            # Later, we'll elaborate on the tests. For now, some basic checks
            assert response.status_code == 200
            assert set(response.data.keys()) == set(
                ['count', 'next', 'previous', 'results'])

            results = response.data['results']
            assert len(results) == len(self.users)
            enrollments = get_course_enrollments_for_site(self.site)
            assert enrollments.count() == len(self.course_enrollments)

            for rec in results:
                assert set(rec.keys()) == set(self.expected_result_keys)
                assert rec['courses']
                courses = rec['courses']
                # fail if we cannot find the user in the models
                user = get_user_model().objects.get(username=rec['username'])
                user_course_enrollments = enrollments.filter(user=user)
                # Check that each course enrollment is represented
                assert len(rec['courses']) == user_course_enrollments.count()
                for ce in user_course_enrollments:
                    assert get_course_rec(ce.course_id, rec['courses'])
