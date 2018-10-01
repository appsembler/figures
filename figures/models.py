'''
Defines Figures models

'''

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from model_utils.models import TimeStampedModel


@python_2_unicode_compatible
class CourseDailyMetrics(TimeStampedModel):
    '''Metrics data specific to an individual course

    '''
    date_for = models.DateField()

    # Leaving as a simple string for initial development
    # TODO: Follow on to decide if we want to make this an FK to
    # the CourseOverview model or have the course_id be a
    # CourseKeyField
    course_id = models.CharField(max_length=255)

    enrollment_count = models.IntegerField()
    active_learners_today = models.IntegerField()
    # Do we want cumulative average progress for the month?
    average_progress = models.DecimalField(
        max_digits=2, decimal_places=2, blank=True, null=True)
    average_days_to_complete = models.IntegerField(blank=True, null=True)
    num_learners_completed = models.IntegerField()

    class Meta:
        unique_together = ('course_id', 'date_for',)
        ordering = ('date_for', 'course_id',)

    # Any other data we want?

    def __str__(self):
        return "id:{}, date_for:{}, course_id:{}".format(
            self.id, self.date_for, self.course_id)


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
