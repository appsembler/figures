'''Serializers used in Figures

'''

from django_countries import Countries
from rest_framework import serializers
from rest_framework.fields import empty

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)

from student.models import CourseAccessRole, CourseEnrollment

from figures.helpers import as_course_key
from figures.models import CourseDailyMetrics, SiteDailyMetrics


##
## Serializer Field classes
##

class SerializeableCountryField(serializers.ChoiceField):
    '''
    This class addresses an issue with django_countries that does not serialize
    blank country values. See here:

        https://github.com/SmileyChris/django-countries/issues/106
    '''
    def __init__(self, **kwargs):
        super(SerializeableCountryField, self).__init__(choices=Countries(),
            **kwargs)

    def to_representation(self, value):
        if value in ('', None):
            # normally here it would return value.
            # which is Country(u'') and not serialiable
            # See the issue linked in the class docstring
            return ''

        return super(SerializeableCountryField, self).to_representation(value)


###
### Summary serializers for listing
###

class CourseIndexSerializer(serializers.Serializer):
    '''Provides a limited set of course overview information

    The full set returned by the edx-platform built-in course api can be found
    in this class:

        lms.djangoapps.course_api.serializers.CourseSerializer
    '''

    id = serializers.CharField()
    name = serializers.CharField(source='display_name_with_default_escaped')
    org = serializers.CharField(source='display_org_with_default')
    number = serializers.CharField(source='display_number_with_default')


class UserIndexSerializer(serializers.Serializer):
    '''Provides a limited set of user information for summary display
    '''
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    fullname = serializers.CharField(source='profile.name', default=None,
        read_only=True)


###
### Serializers for edx-platform models
###

class CourseOverviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseOverview
        fields = (
            'id', 'display_name', 'org',
        )


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    '''Provides CourseOverview model based serialization

    '''
    course = CourseOverviewSerializer(read_only=True)
    user = UserIndexSerializer(read_only=True)
    class Meta:
        model = CourseEnrollment
        editable = False


###
### Figures model serializers
###

class CourseDailyMetricsSerializer(serializers.ModelSerializer):
    '''Provides summary data about a specific course
    '''
    average_progress = serializers.DecimalField(max_digits=2, decimal_places=2)
    class Meta:
        model = CourseDailyMetrics


class SiteDailyMetricsSerializer(serializers.ModelSerializer):
    '''Proviedes summary data about the LMS site
    '''

    class Meta:
        model = SiteDailyMetrics


##
## Serializers for serving the front end views
##


class CourseAccessRoleForGCDSerializer(serializers.ModelSerializer):
    '''Serializer to return course staff data for GeneralCourseData
    '''

    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    fullname = serializers.CharField(source='user.profile.name', default=None,
        read_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = CourseAccessRole
        fields = ['user_id', 'username', 'fullname', 'role']


class GeneralCourseDataSerializer(serializers.Serializer):
    '''

    Returns data in the format::

        [
            {
                "course_id": "A101+SomethingSomething",
                "course_name": "This is the course name",
                "course_code": "A101",
                "course_mode": "Something",
                "org": "MyOrganization",
                "start_date": "2017-07-15T16:59:51.740702Z", // can be empty
                "end_date": "2017-07-15T16:59:51.740702Z", // can be empty
                "self_paced": false,
                "staff": [
                    {
                        "username": "matej",
                        "fullname": "Matej Grozdanovic",
                        "user_id": 123,
                        "role": "instructor"
                    },
                    {
                        "username": "bubba",
                        "fullname": "Bubba Brown",
                        "user_id": 42,
                        "role": "staff"
                    }
                ],
                "metrics": {
                    "learners_enrolled": 123,
                    "average_progress": 0.39, // percentage
                    "average_completion_time": "some_time_in_standardised_format",
                    "users_completed": 493, // total number of users that have completed the course since the course was created
                }
            },
            ...
        ]

    '''
    course_id = serializers.CharField(source='id', read_only=True)
    course_name = serializers.CharField(source='display_name_with_default_escaped',
        read_only=True)
    course_code = serializers.CharField(source='display_number_with_default',
        read_only=True)
    org = serializers.CharField(source='display_org_with_default',
        read_only=True)
    start_date = serializers.DateTimeField(source='enrollment_start',
        read_only=True, default=None)
    end_date = serializers.DateTimeField(source='enrollment_end',
        read_only=True, default=None)
    self_paced = serializers.BooleanField(read_only=True)

    staff = serializers.SerializerMethodField()

    metrics = serializers.SerializerMethodField()

    def get_staff(self, obj):
        qs = CourseAccessRole.objects.filter(course_id=obj.id)
        if qs:
            return [CourseAccessRoleForGCDSerializer(data).data for data in qs]
        else:
            return []

    def get_metrics(self, obj):
        qs = CourseDailyMetrics.objects.filter(course_id=str(obj.id))
        if qs:
            return CourseDailyMetricsSerializer(qs.latest('date_for')).data
        else:
            return []


class GeneralUserDataSerializer(serializers.Serializer):
    '''

    Example from API docs:
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

    Changes from spec:
    courses list:
    - uses 'id' instead of 'course_id'
    - includes additional fields, org and number, as we are reusing the 
    CourseIndexSerializer
    '''

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    fullname = serializers.CharField(source='profile.name', default=None,
        read_only=True)

    country = SerializeableCountryField(source='profile.country',
        required=False, read_only=True, allow_blank=True)
    is_active = serializers.BooleanField(read_only=True)
    year_of_birth = serializers.IntegerField(source='profile.year_of_birth', read_only=True)
    gender = serializers.CharField(source='profile.gender', read_only=True)
    date_joined = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    level_of_education = serializers.CharField(source='profile.level_of_education', 
        allow_blank=True, required=False, read_only=True)

    language_proficiencies = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    def get_language_proficiencies(self, user):
        if hasattr(user,'profiles') and user.profile.language:
            return [user.profile.language]
        else:
            return []

    def get_courses(self, user):
        course_ids = CourseEnrollment.objects.filter(
            user=user).values_list('course_id', flat=True).distinct()

        course_overviews = CourseOverview.objects.filter(
            id__in=[as_course_key(course_id) for course_id in course_ids])

        return [CourseOverviewSerializer(data).data for data in course_overviews]
