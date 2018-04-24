'''
Defines edx-figures models

'''

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from model_utils.models import TimeStampedModel


@python_2_unicode_compatible
class SiteDailyMetrics(TimeStampedModel):
    '''
    TODO: Add Multi-site support
    add FK to site and make site + date_for unique together
    '''

    # Date for which this record's data are collected
    date_for = models.DateField(unique=True)
    cumulative_active_user_count = models.IntegerField(blank=True, null=True)
    todays_active_user_count = models.IntegerField(blank=True, null=True)
    total_user_count = models.IntegerField()
    course_count = models.IntegerField()
    total_enrollment_count = models.IntegerField()

    # Foreign key relationships
    # site = 

    class Meta:
        ordering = ['-date_for']

    def __str__(self):
        return "{} {}".format(self.id, self.date_for)
