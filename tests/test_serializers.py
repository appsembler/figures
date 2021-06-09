'''Tests Figures serializer classes

'''

from __future__ import absolute_import
import datetime
from dateutil.parser import parse as dateutil_parse
from decimal import Decimal
from dateutil.parser import parse
import pytest
import pytz

from django.contrib.sites.models import Site
from django.db import models
from django.utils.timezone import utc
from rest_framework.exceptions import ValidationError

from figures.compat import CourseEnrollment
from figures.models import (
    CourseDailyMetrics,
    CourseMauMetrics,
    LearnerCourseGradeMetrics,
    SiteDailyMetrics,
    SiteMauMetrics,
)
from figures.serializers import (
    CourseDailyMetricsSerializer,
    CourseDetailsSerializer,
    CourseEnrollmentSerializer,
    CourseMauMetricsSerializer,
    CourseMauLiveMetricsSerializer,
    EnrollmentDataSerializer,
    GeneralCourseDataSerializer,
    GeneralUserDataSerializer,
    LearnerCourseDetailsSerializer,
    LearnerDetailsSerializer,
    SerializeableCountryField,
    SiteDailyMetricsSerializer,
    SiteMauMetricsSerializer,
    SiteMauLiveMetricsSerializer,
    UserIndexSerializer,
)

from tests.factories import (
    CourseAccessRoleFactory,
    CourseDailyMetricsFactory,
    CourseEnrollmentFactory,
    CourseMauMetricsFactory,
    CourseOverviewFactory,
    EnrollmentDataFactory,
    GeneratedCertificateFactory,
    LearnerCourseGradeMetricsFactory,
    SiteDailyMetricsFactory,
    SiteMauMetricsFactory,
    UserFactory,
    SiteFactory,
    )

from tests.helpers import platform_release
import six


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
        assert parse(data['start_date']) == self.course_overview.start
        assert parse(data['end_date']) == self.course_overview.end
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
        # self.special_fields = set(['course', 'created', 'user', 'course_overview' ])
        self.special_fields = set(['created', 'user', 'course_id' ])
        self.expected_results_keys = set(
            ['id', 'user', 'created', 'is_active', 'mode', 'course_id' ])
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
        # assert data['course']['id'] == str(self.model_obj.course.id)
        # assert data['course']['display_name'] == self.model_obj.course.display_name
        # assert data['course']['org'] == self.model_obj.course.org

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
        check_fields = self.expected_results_keys - self.date_fields - set(['site'])
        for field_name in check_fields:
            db_field = getattr(self.metrics, field_name)
            if type(db_field) in (float, Decimal, ):
                assert float(data[field_name]) == pytest.approx(db_field)
            else:
                assert data[field_name] == db_field

    @pytest.mark.parametrize('average_progress', [0, 0.00, 0.5, 1.0, 1.00])
    def test_average_progress_valid(self, average_progress):
        obj = CourseDailyMetricsFactory(average_progress=average_progress)
        serializer = CourseDailyMetricsSerializer(instance=obj)
        check_val = Decimal(average_progress).quantize(Decimal('.00'))
        data = serializer.data
        assert data['average_progress'] == six.text_type(check_val)

    @pytest.mark.xfail
    @pytest.mark.parametrize('average_progress', [-1.0, 9.0])
    def test_average_progress_not_valid(self, average_progress):
        obj = CourseDailyMetricsFactory(average_progress=average_progress)
        serializer = CourseDailyMetricsSerializer(instance=obj)
        with pytest.raises(ValidationError):
            data = serializer.data


@pytest.mark.django_db
class TestSiteDailyMetricsSerializer(object):
    '''Ttests the SiteDailyMetricsSerializer serializer class
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        '''

        '''
        self.site = Site.objects.first()
        self.date_fields = set(['date_for', 'created', 'modified',])
        self.expected_results_keys = set([o.name for o in SiteDailyMetrics._meta.fields])
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
        check_fields = self.expected_results_keys - self.date_fields - set(['site'])
        for field_name in check_fields:
            assert data[field_name] == getattr(self.site_daily_metrics,field_name)

    @pytest.mark.skip('Saving is not working after removing default site')
    def test_save(self):
        """Make sure we can save serializer data to the model

        """
        assert SiteDailyMetrics.objects.count() == 1
        data = dict(
            site=self.site,
            date_for='2020-01-01',
            cumulative_active_user_count=1,
            todays_active_user_count=2,
            total_user_count=3,
            course_count=4,
            total_enrollment_count=5
        )
        serializer = SiteDailyMetricsSerializer(data=data)
        assert serializer.is_valid()
        serializer.save()
        assert SiteDailyMetrics.objects.count() == 2


@pytest.mark.django_db
class TestEnrollmentDataSerializer(object):
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.enrollment_data = EnrollmentDataFactory()
        self.expected_fields = [
            'id', 'course_id', 'date_enrolled', 'is_enrolled', 'is_completed',
            'progress_percent', 'progress_details',
        ]
        self.date_enrolled_format = '%Y-%m-%d'

    def test_serialize(self):
        """Test Serializing EnrollmentData model with EnrollmentDataSerializer

        Minimal test after bug fix for https://github.com/appsembler/figures/issues/364
        """
        expected_date_enrolled = self.enrollment_data.date_enrolled.strftime(
            self.date_enrolled_format)
        serializer = EnrollmentDataSerializer(self.enrollment_data)
        assert set(serializer.data.keys()) == set(self.expected_fields)
        assert serializer.data['date_enrolled'] == expected_date_enrolled


@pytest.mark.django_db
class TestGeneralCourseDataSerializer(object):
    '''
    TODO: Verify that learner roles are NOT in CourseAccessRole
    If learner roles can be in this model, then we need to add test for verifying
    that learner roles are not in the staff list of the general course data
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = Site.objects.first()
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
        assert parse(data['start_date']) == self.course_overview.start
        assert parse(data['end_date']) == self.course_overview.end
        assert data['self_paced'] == self.course_overview.self_paced

    def test_get_metrics_with_cdm_records(self):
        '''Tests we get the data for the latest CourseDailyMetrics object
        '''
        dates = ['2018-01-01', '2018-02-01',]
        [CourseDailyMetricsFactory(site=self.site,
                                   course_id=self.course_overview.id,
                                   date_for=date) for date in dates]
        data = self.serializer.get_metrics(self.course_overview)
        assert data['date_for'] == dates[-1]

    def test_get_metrics_with_no_cdm_records(self):
        data = self.serializer.get_metrics(self.course_overview)
        assert not data


class TestGeneralUserDataSerializer(object):
    '''Tests the UserIndexSerializer serializer class
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.a_datetime = datetime.datetime(2018, 2, 2, tzinfo=pytz.UTC)
        self.user_attributes = {
            'username': 'alpha_one',
            'email': 'alpha_one@example.com',
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
            'id', 'username', 'email', 'fullname','country', 'is_active', 'gender',
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
        assert data['email'] == 'alpha_one@example.com'
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
        self.site = Site.objects.first()
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

    def test_get_progress_data(self):
        """
        Method should return data of the form:
            {'course_progress_history': [],
             'course_progress_details': {
                 'sections_worked': 5,
                 'points_possible': 30.0,
                 'sections_possible': 10,
                 'points_earned': 15.0
             },
             'course_progress': (0.5,),
             'course_completed': datetime.datetime(2018, 4, 1, 0, 0, tzinfo=<UTC>)
            }
        """
        metrics_data = dict(
            points_possible=1,
            points_earned=2,
            sections_worked=3,
            sections_possible=4)
        lcgm = LearnerCourseGradeMetricsFactory(
                user=self.course_enrollment.user,
                course_id=str(self.course_enrollment.course_id),
                **metrics_data
                )

        data = self.serializer.get_progress_data(self.course_enrollment)
        details = data['course_progress_details']
        for key, val in metrics_data.items():
            assert details[key] == val
        assert data['course_progress'] == lcgm.progress_percent
        assert data['course_completed'] == self.generated_certificate.created_date

    def test_get_progress_data_with_no_data(self):
        """Tests that the serializer method succeeds when no learner course
        grade metrics records
        """
        expected_data = {
            'course_progress_history': [],
            'course_progress_details': None,
            'course_progress': 0.0,
            'course_completed': False
        }
        assert not LearnerCourseGradeMetrics.objects.count()
        course_enrollment = CourseEnrollmentFactory()
        data = self.serializer.get_progress_data(course_enrollment)
        assert data == expected_data


@pytest.mark.django_db
class TestLearnerDetailsSerializer(object):
    '''Tests the LearnerDetailSerializer serializer class
    '''

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = Site.objects.first()
        self.user_attributes = {
            'username': 'alpha_one',
            'profile__name': 'Alpha One',
            'profile__country': 'CA',
        }
        self.user = UserFactory(**self.user_attributes)
        self.serializer = LearnerDetailsSerializer(
            instance=self.user, context=dict(site=self.site))

    def test_has_fields(self):
        '''Tests that the serialized UserIndex data has specific keys and values

        We use a set instead of just doing this:

            assert data.keys() == ['id', 'username', 'fullname', ]

        because we can't guarentee order. See:
            https://docs.python.org/2/library/stdtypes.html#dict.items
        '''
        expected_fields = set([
        'id', 'username', 'name', 'email', 'country', 'is_active', 'year_of_birth',
        'level_of_education', 'gender', 'date_joined', 'bio', 'courses',
        'language_proficiencies', 'profile_image'
        ])
        data = self.serializer.data
        assert set(data.keys()) == expected_fields
        
        # This is to make sure that the serializer retrieves the correct nested
        # model (UserProfile) data
        assert data['name'] == 'Alpha One'

    @pytest.mark.skip(reason='Not implemented')
    def test_excludes_other_sites(self):
        """
        Need to make sure that only courses for the requesting site are returned
        """
        pass


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


@pytest.mark.django_db
class TestCourseMauMetricsSerializer(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.model = CourseMauMetrics
        self.obj = CourseMauMetricsFactory(mau=42)
        self.serializer_class = CourseMauMetricsSerializer

    def test_serialize(self):
        serializer = self.serializer_class(self.obj)
        data = serializer.data
        assert data['mau'] == self.obj.mau
        assert data['domain'] == self.obj.site.domain
        assert data['course_id'] == self.obj.course_id
        assert dateutil_parse(data['date_for']).date() == self.obj.date_for 


@pytest.mark.django_db
class TestSiteMauMetricsSerializer(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.model = SiteMauMetrics
        self.obj = SiteMauMetricsFactory(mau=42)
        self.serializer_class = SiteMauMetricsSerializer

    def test_serialize(self):
        serializer = self.serializer_class(self.obj)
        data = serializer.data
        assert data['mau'] == self.obj.mau
        assert data['domain'] == self.obj.site.domain
        assert dateutil_parse(data['date_for']).date() == self.obj.date_for 



@pytest.mark.django_db
class TestCourseMauLiveMetricsSerializer(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        pass

    def test_serialize(self):
        site = SiteFactory()
        course_overview = CourseOverviewFactory()
        in_data = dict(
            month_for=datetime.date(2019, 10, 29),
            count=42,
            course_id=str(course_overview.id),
            domain=u'wookie.example.com'
        )

        serializer = CourseMauLiveMetricsSerializer(in_data)
        out_data = serializer.data
        assert set(out_data.keys()) == set(in_data.keys())
        assert out_data['count'] == in_data['count']
        assert dateutil_parse(out_data['month_for']).date() == in_data['month_for']
        assert out_data['domain'] == in_data['domain']
        assert out_data['course_id'] == in_data['course_id']


@pytest.mark.django_db
class TestSiteMauLiveMetricsSerializer(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        pass

    def test_serialize(self):
        site = SiteFactory()
        in_data = dict(
            month_for=datetime.date(2019, 10, 29),
            count=42,
            domain=site.domain,
        )

        serializer = SiteMauLiveMetricsSerializer(in_data)

        in_data = dict(
            month_for=datetime.date(2019, 10, 29),
            count=42,
            domain=u'wookie.example.com'
        )

        serializer = SiteMauLiveMetricsSerializer(in_data)
        out_data = serializer.data
        assert set(out_data.keys()) == set(in_data.keys())
        assert out_data['count'] == in_data['count']
        assert dateutil_parse(out_data['month_for']).date() == in_data['month_for']
        assert out_data['domain'] == in_data['domain']
