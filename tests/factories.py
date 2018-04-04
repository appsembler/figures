'''
Helpers to generate fixtures for testing.

Uses Factory Boy: https://factoryboy.readthedocs.io/en/latest/

'''

import factory
from factory.django import DjangoModelFactory

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)


class CourseOverviewFactory(DjangoModelFactory):
    class Meta:
        model = CourseOverview

    # Only define the fields that we will retrieve
    id = factory.Sequence(lambda n: 'course-v1:StarFleetAcademy+SFA{}+2161'.format(n))
    display_name = factory.Sequence(lambda n: 'SFA Course {}'.format(n))
    org = 'StarFleetAcademy'
    number = '2161'
