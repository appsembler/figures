'''Tests Figures serializer classes

'''

import datetime
from dateutil.parser import parse as dateutil_parse
from decimal import Decimal
import pytest
import pytz

from django.db import models

from student.models import CourseEnrollment

from figures.models import CourseDailyMetrics, SiteDailyMetrics
from figures.serializers import (
    CourseDailyMetricsSerializer,
    CourseEnrollmentSerializer,
    SiteDailyMetricsSerializer,
    UserIndexSerializer,
    GeneralUserDataSerializer,
)

from tests.factories import (
    CourseDailyMetricsFactory,
    CourseEnrollmentFactory,
    SiteDailyMetricsFactory,
    UserFactory,
    )

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


class TestCourseEnrollmentSerializer(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.model =  CourseEnrollment
        self.special_fields = set(['course_id', 'created', 'user', ])
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
class TestGeneralUserDataSerializer(object):
    '''Tests the UserIndexSerializer serializer class
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.a_datetime = datetime.datetime(2018, 02, 02, tzinfo=pytz.UTC)
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

        #import pdb; pdb.set_trace()
        assert set(data.keys()) == set(self.expected_fields)
        
        # This is to make sure that the serializer retrieves the correct nested
        # model (UserProfile) data
        assert data['username'] == 'alpha_one'
        assert data['fullname'] == 'Alpha One'
        assert data['country'] == 'CA'
        assert data['gender'] == 'o'
        assert data['date_joined'] == str(self.a_datetime.date())

