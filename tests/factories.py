'''
Helpers to generate fixtures for testing.

Uses Factory Boy: https://factoryboy.readthedocs.io/en/latest/

'''

from django.contrib.auth import get_user_model
#from django_countries.fields import CountryField
import factory
from factory.django import DjangoModelFactory

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)

from student.models import UserProfile
from lms.djangoapps.teams.models import CourseTeam, CourseTeamMembership


class CourseOverviewFactory(DjangoModelFactory):
    class Meta:
        model = CourseOverview

    # Only define the fields that we will retrieve
    id = factory.Sequence(lambda n: 'course-v1:StarFleetAcademy+SFA{}+2161'.format(n))
    display_name = factory.Sequence(lambda n: 'SFA Course {}'.format(n))
    org = 'StarFleetAcademy'
    number = '2161'
    display_org_with_default = factory.LazyAttribute(lambda o: o.org)


class CourseTeamFactory(DjangoModelFactory):
    class Meta:
        model = CourseTeam

    name = factory.Sequence(lambda n: "CourseTeam #%s" % n)


class CourseTeamMembershipFactory(DjangoModelFactory):
    class Meta:
        model = CourseTeamMembership


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    # User full name
    name = factory.Sequence(lambda n: 'User Name{}'.format(n))
    country = 'US'


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'user{}'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_active = True
    is_staff = False

    profile = factory.RelatedFactory(UserProfileFactory,
        'user',)

    @factory.post_generation
    def teams(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for team in extracted:
                self.teams.add(team)
