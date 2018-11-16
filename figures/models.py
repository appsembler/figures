"""Defines Figures models

"""

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from jsonfield import JSONField

from model_utils.models import TimeStampedModel


@python_2_unicode_compatible
class CourseDailyMetrics(TimeStampedModel):
    """Metrics data specific to an individual course

    """
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
    """
    TODO: Add Multi-site support
    add FK to site and make site + date_for unique together
    """

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


class LearnerCourseGradeMetricsManager(models.Manager):
    """Custom model manager for LearnerCourseGrades model
    """
    def most_recent_for_learner_course(self, user, course_id):
        return self.filter(
            user=user, course_id=str(course_id)).order_by('-date_for').first()


@python_2_unicode_compatible
class LearnerCourseGradeMetrics(TimeStampedModel):
    """This model stores metrics for a learner and course on a given date

    THIS MODEL IS EVOLVING

    Purpose is primarliy to improve performance for the front end. In addition,
    data collected can be used for course progress over time

    We're capturing data from figures.metrics.LearnerCourseGrades

    Note: We're probably going to move ``LearnerCourseGrades`` to figures.pipeline
    since that class will only be needed by the pipeline

    Even though this is for a course enrollment, we're mapping to the user
    and providing course id instead of an FK relationship to the courseenrollment
    Reason is we're likely more interested in the learner and the course than the specific
    course enrollment. Also means that the Figures models do not have a hard
    dependency on models in edx-platform

    Considered using DecimalField for points as we can control the decimal places
    But for now, using float, as I'm not entirely sure how many decimal places are
    actually needed and edx-platform uses FloatField in its grades models

    """
    date_for = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    course_id = models.CharField(max_length=255, blank=True)

    points_possible = models.FloatField()
    points_earned = models.FloatField()
    sections_worked = models.IntegerField()
    sections_possible = models.IntegerField()

    objects = LearnerCourseGradeMetricsManager()

    class Meta:
        unique_together = ('user', 'course_id', 'date_for',)
        ordering = ('date_for', 'user__username', 'course_id',)

    def __str__(self):
        return "{} {} {} {}".format(
            self.id, self.date_for, self.user.username, self.course_id)

    @property
    def progress_percent(self):
        """Returns the sections worked divided by the sections possible

        If sections possible is zero then returns 0

        Sections possible can be zero when there are no graded sections in a
        course.
        """
        if self.sections_possible:
            return float(self.sections_worked) / float(self.sections_possible)
        else:
            return 0.0

    @property
    def progress_details(self):
        """This method gets the progress details.
        This method is a temporary fix until the serializers are updated.
        """
        return dict(
            points_possible=self.points_possible,
            points_earned=self.points_earned,
            sections_worked=self.sections_worked,
            sections_possible=self.sections_possible,
        )


class PipelineError(TimeStampedModel):
    """
    Captures errors when running Figures pipeline.

    TODO: Add organization foreign key when we add multi-tenancy
    """
    UNSPECIFIED_DATA = 'UNSPECIFIED'
    GRADES_DATA = 'GRADES'
    COURSE_DATA = 'COURSE'
    SITE_DATA = 'SITE'

    ERROR_TYPE_CHOICES = (
        (UNSPECIFIED_DATA, 'Unspecified data error'),
        (GRADES_DATA, 'Grades data error'),
        (COURSE_DATA, 'Course data error'),
        (SITE_DATA, 'Site data error'),
        )
    error_type = models.CharField(
        max_length=255, choices=ERROR_TYPE_CHOICES, default=UNSPECIFIED_DATA)
    error_data = JSONField()
    # Attributes for convenient querying
    course_id = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return "{}, {}, {}".format(self.id, self.created, self.error_type)
