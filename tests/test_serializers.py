'''Tests Figures serializer classes

'''

import datetime
from dateutil.parser import parse as dateutil_parse
from decimal import Decimal
from dateutil.parser import parse
import pytest
import pytz

from django.db import models
from django.utils.timezone import utc

from student.models import CourseEnrollment

from figures.models import CourseDailyMetrics, SiteDailyMetrics
from figures.serializers import (
    CourseDailyMetricsSerializer,
    CourseDetailsSerializer,
    CourseEnrollmentSerializer,
    GeneralCourseDataSerializer,
    GeneralUserDataSerializer,
    LearnerCourseDetailsSerializer,
    LearnerDetailsSerializer,
    SerializeableCountryField,
    SiteDailyMetricsSerializer,
    UserIndexSerializer,
)

from tests.factories import (
    CourseAccessRoleFactory,
    CourseDailyMetricsFactory,
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    GeneratedCertificateFactory,
    SiteDailyMetricsFactory,
    UserFactory,
    )


class TestSerializableCountryField(object):

    @pytest.mark.parametrize('value, expected_result', [
            ('abc', 'abc'),
            ('', ''),
            (None, ''),
        ])
    def test_representation(self, value, expected_result):
        '''This tests the missing coverage in ``to_representation`` when
        the country field is blank. We don't need a real Countries object, we
        can test with any string

        '''
        assert SerializeableCountryField().to_representation(value) == expected_result


@pytest.mark.django_db
class TestUserIndexSerializer(object):
    '''Tests the UserIndexSerializer serializer class
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.user_attributes = {
            'username': 'alpha_one',
            'profile__name': 'Alpha One',
            'profile__country': 'CA',
        }
        self.user = UserFactory(**self.user_attributes)
        self.serializer = UserIndexSerializer(instance=self.user)

    def test_has_fields(self):
        '''Tests that the serialized UserIndex data has specific keys and values
        
        We use a set instead of just doing this:

            assert data.keys() == ['id', 'username', 'fullname', ]

        because we can't guarentee order. See:
            https://docs.python.org/2/library/stdtypes.html#dict.items
        '''
        data = self.serializer.data

        assert set(data.keys()) == set(['id', 'username', 'fullname', ])
        
        # This is to make sure that the serializer retrieves the correct nested
        # model (UserProfile) data
        assert data['fullname'] == 'Alpha One'


class TestCourseDetailsSerializer(object):
    '''
    Needs more work
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.course_overview = CourseOverviewFactory()
        self.users = [UserFactory(), UserFactory()]

        self.course_access_roles  = [
            CourseAccessRoleFactory(
                user=self.users[0],
                course_id=self.course_overview.id,
                role='staff'),
            CourseAccessRoleFactory(
                user=self.users[1],
                course_id=self.course_overview.id,
                role='administrator'),
        ]
        self.serializer = CourseDetailsSerializer(instance=self.course_overview)

        self.expected_fields = [
            'course_id', 'course_name', 'course_code','org', 'start_date',
            'end_date', 'self_paced', 'staff', 'average_progress',
            'learners_enrolled', 'average_days_to_complete', 'users_completed',

        ]

    def test_has_fields(self):
        data = self.serializer.data
        assert set(data.keys()) == set(self.expected_fields)

        # This is to make sure that the serializer retrieves the correct nested
        # model (UserProfile) data
        assert data['course_id'] == str(self.course_overview.id)
        assert data['course_name'] == self.course_overview.display_name
        assert data['course_code'] == self.course_overview.number
        assert data['org'] == self.course_overview.org
        assert parse(data['start_date']) == self.course_overview.enrollment_start
        assert parse(data['end_date']) == self.course_overview.enrollment_end
        assert data['self_paced'] == self.course_overview.self_paced

    def test_get_staff_with_no_course(self):
        '''Create a serializer for a course with a different ID than for the
        data we set up. This simulates when there are no staff members for the
        given course, which will have a different ID than the one we created in
        the setup method
        '''
        assert CourseDetailsSerializer().get_staff(CourseOverviewFactory()) == []


class TestCourseEnrollmentSerializer(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.model =  CourseEnrollment
        self.special_fields = set(['course_id', 'created', 'user', 'course_overview' ])
        self.expected_results_keys = set([o.name for o in self.model._meta.fields])
        field_names = (o.name for o in self.model._meta.fields
            if o.name not in self.date_fields )
        self.model_obj = CourseEnrollmentFactory()
        self.serializer = CourseEnrollmentSerializer(instance=self.model_obj)

    def test_has_fields(self):
        '''
        Initially, doing a limited test of fields as figure out how mamu of the
        CourseEnrollment model fields and relationships we need to capture.
        '''
        data = self.serializer.data
        assert data['course_id'] == str(self.model_obj.course_id)
        assert dateutil_parse(data['created']) == self.model_obj.created
        assert data['user']['fullname'] == self.model_obj.user.profile.name

        for field_name in (self.expected_results_keys - self.special_fields):
            db_field = getattr(self.model_obj, field_name)
            if type(db_field) in (float, Decimal, ):
                assert float(data[field_name]) == pytest.approx(db_field)
            else:
                assert data[field_name] == db_field


@pytest.mark.django_db
class TestCourseDailyMetricsSerializer(object):
    '''Tests the CourseDailyMetricsSerializer serializer class

    TODO: After we complete the initial PRs for the site and course metrics
    models/serializers/views and tests, DRY up the test code
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.model = CourseDailyMetrics
        self.date_fields = set(['date_for', 'created', 'modified',])
        self.expected_results_keys = set([o.name for o in self.model._meta.fields])
        field_names = (o.name for o in self.model._meta.fields
            if o.name not in self.date_fields )
        self.metrics = CourseDailyMetricsFactory()
        self.serializer = CourseDailyMetricsSerializer(instance=self.metrics)

    @pytest.mark.skip(reason='Test not implemented yet')
    def test_time_zone(self):
        pass

    def test_has_fields(self):
        '''Verify the serialized data has the same keys and values as the model

        Django 2.0 has a convenient method, 'Cast' that will simplify converting
        values:
        https://docs.djangoproject.com/en/2.0/ref/models/database-functions/#cast

        This means that we can retrieve the model instance values as a dict
        and do a simple ``assert self.serializer.data == queryset.values(...)``
        '''

        data = self.serializer.data

        # Hack: Check date and datetime values explicitly
        assert data['date_for'] == str(self.metrics.date_for)
        assert dateutil_parse(data['created']) == self.metrics.created
        assert dateutil_parse(data['modified']) == self.metrics.modified

        for field_name in (self.expected_results_keys - self.date_fields):
            db_field = getattr(self.metrics, field_name)
            if type(db_field) in (float, Decimal, ):
                assert float(data[field_name]) == pytest.approx(db_field)
            else:
                assert data[field_name] == db_field


@pytest.mark.django_db
class TestSiteDailyMetricsSerializer(object):
    '''Ttests the SiteDailyMetricsSerializer serializer class
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        '''

        '''
        self.date_fields = set(['date_for', 'created', 'modified',])
        self.expected_results_keys = set([o.name for o in SiteDailyMetrics._meta.fields])
        field_names = (o.name for o in SiteDailyMetrics._meta.fields
            if o.name not in self.date_fields )
        self.site_daily_metrics = SiteDailyMetricsFactory()
        self.serializer = SiteDailyMetricsSerializer(
            instance=self.site_daily_metrics)

    @pytest.mark.skip(reason='Test not implemented yet')
    def test_time_zone(self):
        pass

    def test_has_fields(self):
        '''Verify the serialized data has the same keys and values as the model

        Django 2.0 has a convenient method, 'Cast' that will simplify converting
        values:
        https://docs.djangoproject.com/en/2.0/ref/models/database-functions/#cast

        This means that we can retrieve the model instance values as a dict
        and do a simple ``assert self.serializer.data == queryset.values(...)``
        '''

        data = self.serializer.data

        # Hack: Check date and datetime values explicitly
        assert data['date_for'] == str(self.site_daily_metrics.date_for)
        assert dateutil_parse(data['created']) == self.site_daily_metrics.created
        assert dateutil_parse(data['modified']) == self.site_daily_metrics.modified

        for field_name in (self.expected_results_keys - self.date_fields):
            assert data[field_name] == getattr(self.site_daily_metrics,field_name)


@pytest.mark.django_db
class TestGeneralCourseDataSerializer(object):
    '''
    TODO: Verify that learner roles are NOT in CourseAccessRole
    If learner roles can be in this model, then we need to add test for verifying
    that learner roles are not in the staff list of the general course data
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.course_overview = CourseOverviewFactory()
        self.users = [ UserFactory(), UserFactory()]
        self.course_access_roles = [
            CourseAccessRoleFactory(user=self.users[0],
                                    course_id=self.course_overview.id,
                                    role='staff'),
            CourseAccessRoleFactory(user=self.users[1],
                                    course_id=self.course_overview.id,
                                    role='administrator'),
        ]
        self.serializer = GeneralCourseDataSerializer(instance=self.course_overview)
        self.expected_fields = [
            'course_id', 'course_name', 'course_code', 'org', 'start_date',
            'end_date', 'self_paced', 'staff', 'metrics',
        ]

    def test_has_fields(self):
        '''Tests that the serialized general course  data has specific keys and values
        '''
        data = self.serializer.data
        assert set(data.keys()) == set(self.expected_fields)

        # This is to make sure that the serializer retrieves the correct nested
        # model (UserProfile) data
        assert data['course_id'] == str(self.course_overview.id)
        assert data['course_name'] == self.course_overview.display_name
        assert data['course_code'] == self.course_overview.number
        assert data['org'] == self.course_overview.org
        assert parse(data['start_date']) == self.course_overview.enrollment_start
        assert parse(data['end_date']) == self.course_overview.enrollment_end
        assert data['self_paced'] == self.course_overview.self_paced

    def test_get_metrics_with_cdm_records(self):
        '''Tests we get the data for the latest CourseDailyMetrics object
        '''
        dates = ['2018-01-01', '2018-02-01',]
        [CourseDailyMetricsFactory(course_id=self.course_overview.id,
                                   date_for=date) for date in dates]
        assert self.serializer.get_metrics(
            self.course_overview)['date_for'] == dates[-1]


class TestGeneralUserDataSerializer(object):
    '''Tests the UserIndexSerializer serializer class
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.a_datetime = datetime.datetime(2018, 2, 2, tzinfo=pytz.UTC)
        self.user_attributes = {
            'username': 'alpha_one',
            'profile__name': 'Alpha One',
            'profile__country': 'CA',
            'profile__gender': 'o',
            'date_joined': self.a_datetime,
            'profile__year_of_birth': 1989,
            'profile__level_of_education': 'other',

        }
        self.user = UserFactory(**self.user_attributes)
        self.serializer = GeneralUserDataSerializer(instance=self.user)

        self.expected_fields = [
            'id', 'username', 'fullname','country', 'is_active', 'gender',
            'date_joined', 'year_of_birth', 'level_of_education', 'courses',
            'language_proficiencies',
        ]

    def test_has_fields(self):
        '''Tests that the serialized UserIndex data has specific keys and values
        
        We use a set instead of just doing this:

            assert data.keys() == ['id', 'username', 'fullname', ]

        because we can't guarentee order. See:
            https://docs.python.org/2/library/stdtypes.html#dict.items
        '''
        data = self.serializer.data

        assert set(data.keys()) == set(self.expected_fields)
        
        # This is to make sure that the serializer retrieves the correct nested
        # model (UserProfile) data
        assert data['username'] == 'alpha_one'
        assert data['fullname'] == 'Alpha One'
        assert data['country'] == 'CA'
        assert data['gender'] == 'o'
        assert data['date_joined'] == str(self.a_datetime.date())


@pytest.mark.django_db
class TestLearnerCourseDetailsSerializer(object):
    '''

    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        # self.model = CourseEnrollment
        # self.user_attributes = {
        #     'username': 'alpha_one',
        #     'profile__name': 'Alpha One',
        #     'profile__country': 'CA',
        # }
        #self.user = UserFactory(**self.user_attributes)
        self.certificate_date = datetime.datetime(2018, 4, 1, tzinfo=utc)
        self.course_enrollment = CourseEnrollmentFactory(
            )
        self.generated_certificate = GeneratedCertificateFactory(
            user=self.course_enrollment.user,
            course_id=self.course_enrollment.course_id,
            created_date=self.certificate_date,
            )
        self.serializer = LearnerCourseDetailsSerializer(
            instance=self.course_enrollment)

    def test_has_fields(self):

        expected_fields = set([
            'course_name', 'course_code', 'course_id', 'date_enrolled',
            'progress_data', 'enrollment_id',
            ])

        data = self.serializer.data
        assert set(data.keys()) == expected_fields


@pytest.mark.django_db
class TestLearnerDetailsSerializer(object):
    '''Tests the LearnerDetailSerializer serializer class
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.user_attributes = {
            'username': 'alpha_one',
            'profile__name': 'Alpha One',
            'profile__country': 'CA',
        }
        self.user = UserFactory(**self.user_attributes)
        self.serializer = LearnerDetailsSerializer(instance=self.user)

    def test_has_fields(self):
        '''Tests that the serialized UserIndex data has specific keys and values

        We use a set instead of just doing this:

            assert data.keys() == ['id', 'username', 'fullname', ]

        because we can't guarentee order. See:
            https://docs.python.org/2/library/stdtypes.html#dict.items
        '''
        expected_fields = set(['id', 'username', 'name', 'country', 'is_active',
            'profile_image', 'courses', 'year_of_birth', 'gender', 'email',
            'level_of_education', 'language_proficiencies', 'date_joined',])
        data = self.serializer.data

        assert set(data.keys()) == expected_fields
        
        # This is to make sure that the serializer retrieves the correct nested
        # model (UserProfile) data
        assert data['name'] == 'Alpha One'


@pytest.mark.django_db
class TestUserIndexSerializer(object):
    '''Tests the UserIndexSerializer serializer class
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.user_attributes = {
            'username': 'alpha_one',
            'profile__name': 'Alpha One',
            'profile__country': 'CA',
        }
        self.user = UserFactory(**self.user_attributes)
        self.serializer = UserIndexSerializer(instance=self.user)

    def test_has_fields(self):
        '''Tests that the serialized UserIndex data has specific keys and values
        
        We use a set instead of just doing this:

            assert data.keys() == ['id', 'username', 'fullname', ]

        because we can't guarentee order. See:
            https://docs.python.org/2/library/stdtypes.html#dict.items
        '''
        data = self.serializer.data

        assert set(data.keys()) == set(['id', 'username', 'fullname', ])
        
        # This is to make sure that the serializer retrieves the correct nested
        # model (UserProfile) data
        assert data['fullname'] == 'Alpha One'
