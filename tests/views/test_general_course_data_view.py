
import pytest

from django.contrib.auth import get_user_model
from django.db.models import F

from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)
from student.models import CourseEnrollment

from figures.helpers import as_course_key
from figures.views import GeneralCourseDataViewSet

from tests.factories import (
    CourseDailyMetricsFactory,
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    UserFactory,
    )

from tests.views.base import BaseViewTest

COURSE_ID_STR_TEMPLATE = 'course-v1:StarFleetAcademy+SFA{}+2161'

USER_DATA = [
    {'id': 100, 'username': u'alpha', 'fullname': u'Alpha One',
     'is_active': True, 'country': 'CA'},
    {'id': 101, 'username': u'alpha02', 'fullname': u'Alpha Two', 'is_active': False, 'country': 'UK'},
    {'id': 102, 'username': u'bravo', 'fullname': u'Bravo One', 'is_active': True, 'country': 'US'},
    {'id': 103, 'username': u'bravo02', 'fullname': u'Bravo Two', 'is_active': True, 'country': 'UY'},
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
        id=kwargs['id'], display_name=kwargs['name'], org=kwargs['org'], number=kwargs['number'])

def make_course_enrollments(user, courses, **kwargs):
    '''
        creates course enrollments for every course in COURSE_DATA for the given user
    '''
    course_enrollments = []
    for course in courses:
        course_enrollments.append(
            CourseEnrollmentFactory(
                course_id=course.id,
                user=user,
                )
            )

@pytest.mark.django_db
class TestGeneralCourseDataViewSet(BaseViewTest):
    '''Tests the UserIndexView view class
    '''

    request_path = 'api/courses/general'
    view_class = GeneralCourseDataViewSet
    @pytest.fixture(autouse=True)
    def setup(self, db):
        super(TestGeneralCourseDataViewSet, self).setup(db)
        self.users = [make_user(**data) for data in USER_DATA]
        self.course_overviews = [make_course(**data) for data in COURSE_DATA]
        #self.course_enrollments = [make_course_enrollments(user, self.course_overviews) for user in self.users]
        #self.course_daily_metrics = [make_course_daily_metrics()]
        self.expected_result_keys = [
            'course_id', 'course_name', 'course_code','org', 'start_date',
            'end_date', 'self_paced', 'staff', 'metrics',
        ]

    # @pytest.mark.parametrize('endpoint, filter', [
    #     ('api/courses/general', {}),
    #     ])
    #def test_get_list(self, endpoint, filter):
    def test_get_list(self):
        '''Tests retrieving a list of users with abbreviated details

        The fields in each returned record are identified by
            `figures.serializers.UserIndexSerializer`
        '''
        request = APIRequestFactory().get(self.request_path)
        force_authenticate(request, user=self.staff_user)
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)

        # Later, we'll elaborate on the tests. For now, some basic checks
        assert response.status_code == 200
        assert set(response.data.keys()) == set(
            ['count', 'next', 'previous', 'results',])
        assert len(response.data['results']) == len(self.course_overviews)

        for rec in response.data['results']:
            course_overview = CourseOverview.objects.get(id=as_course_key(rec['course_id']))

            # Test top level vars
            assert rec['course_name'] == course_overview.display_name

            assert rec['course_id'] == str(course_overview.id)
            # TODO: add asserts for more fields
            # TODO as testing improvement future work: validating metrics and staff
            # We're starting to need more complex data set-up, so deferring to
            # implement a 


