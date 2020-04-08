"""Defines Figures models

"""

from datetime import date
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from jsonfield import JSONField

from model_utils.models import TimeStampedModel


def default_site():
    """
    Wrapper aroung `django.conf.settings.SITE_ID` so we do not have to create a
    new migration if we change how we get the default site ID
    """
    return settings.SITE_ID


@python_2_unicode_compatible
class CourseDailyMetrics(TimeStampedModel):
    """Metrics data specific to an individual course

    CourseDailyMetrics instances are created before the SiteDailyMetrics. This,
    along with the fact we now filter course metrics for a given site, we aren't
    adding a SiteDailyMetrics foreign key. This is subject to change as the code
    evolves.
    """
    site = models.ForeignKey(Site)
    date_for = models.DateField()

    # Leaving as a simple string for initial development
    # TODO: Follow on to decide if we want to make this an FK to
    # the CourseOverview model or have the course_id be a
    # CourseKeyField
    course_id = models.CharField(max_length=255)
    enrollment_count = models.IntegerField()
    active_learners_today = models.IntegerField()
    # Do we want cumulative average progress for the month?

    # TODO: Consider making average progress an int value betwen 0 and 100 if
    # that will save significant storage. Otherwise, we wait for the model
    # abstraction rework
    average_progress = models.DecimalField(
        max_digits=3, decimal_places=2, blank=True, null=True,
        validators=[MaxValueValidator(1.0), MinValueValidator(0.0)],
        )

    average_days_to_complete = models.IntegerField(blank=True, null=True)
    num_learners_completed = models.IntegerField()

    class Meta:
        unique_together = ('course_id', 'date_for',)
        ordering = ('-date_for', 'course_id',)

    # Any other data we want?

    def __str__(self):
        return "id:{}, date_for:{}, course_id:{}".format(
            self.id, self.date_for, self.course_id)

    @classmethod
    def latest_previous_record(cls, site, course_id, date_for=None):
        """
        Get the most recent record before the given date

        This is a convenience method to retrieve the most recent record before
        the date given in the `date_for` argument
        If `date_for` is provided, then the latest date before `date_for` is
        found
        """
        filter_args = dict(site=site, course_id=course_id)

        if date_for:
            filter_args['date_for__lt'] = date_for
        return cls.objects.filter(**filter_args).order_by('-date_for').first()


@python_2_unicode_compatible
class SiteDailyMetrics(TimeStampedModel):
    """
    Stores metrics for a given site and day
    """

    site = models.ForeignKey(Site)
    # Date for which this record's data are collected
    date_for = models.DateField()
    cumulative_active_user_count = models.IntegerField(blank=True, null=True)
    todays_active_user_count = models.IntegerField(blank=True, null=True)
    total_user_count = models.IntegerField()
    course_count = models.IntegerField()
    total_enrollment_count = models.IntegerField()

    class Meta:
        """
        SiteDailyMetrics view and serializer tests fail when we include 'site'
        in the `unique_together` fields:

            unique_together = ['site', 'date_for']

            ValueError: Cannot assign "1": "SiteDailyMetrics.site" must be a
            "Site" instance

        Since we do want to constrain uniqueness per site+day, we'll need to fix
        this
        """
        ordering = ['-date_for', 'site']

    def __str__(self):
        return "id:{}, date_for:{}, site:{}".format(
            self.id, self.date_for, self.site.domain)

    @classmethod
    def latest_previous_record(cls, site, date_for=None):
        """
        Get the most recent record before the given date

        This is a convenience method to retrieve the most recent record before
        the date given in the `date_for` argument
        If `date_for` is provided, then the latest date before `date_for` is
        found
        """
        filter_args = dict(site=site)

        if date_for:
            filter_args['date_for__lt'] = date_for
        return cls.objects.filter(**filter_args).order_by('-date_for').first()


@python_2_unicode_compatible
class SiteMonthlyMetrics(TimeStampedModel):
    """
    Stores metrics for a given site and month


    """

    site = models.ForeignKey(Site)
    # Month for which this record's data are collected
    # Important fields are year and month
    month_for = models.DateField()
    active_user_count = models.IntegerField()

    class Meta:
        ordering = ['-month_for', 'site']
        unique_together = ['month_for', 'site']

    def __str__(self):
        return "id:{}, month_for:{}, site:{}".format(
            self.id, self.month_for, self.site.domain)

    @classmethod
    def add_month(cls, site, year, month, active_user_count, overwrite=False):

        month_for = date(year=year, month=month, day=1)
        if not overwrite:
            try:

                obj = SiteMonthlyMetrics.objects.get(site=site,
                                                     month_for=month_for)
                return (obj, False,)
            except SiteMonthlyMetrics.DoesNotExist:
                pass

        defaults = dict(active_user_count=active_user_count)
        return SiteMonthlyMetrics.objects.update_or_create(site=site,
                                                           month_for=month_for,
                                                           defaults=defaults)


class LearnerCourseGradeMetricsManager(models.Manager):
    """Custom model manager for LearnerCourseGrades model
    """
    def most_recent_for_learner_course(self, user, course_id):
        queryset = self.filter(user=user, course_id=str(course_id))
        return queryset.order_by('-date_for').first()   # pylint: disable=no-member


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
    site = models.ForeignKey(Site)
    date_for = models.DateField()
    # TODO: We should require the user
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


@python_2_unicode_compatible
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
    site = models.ForeignKey(Site, blank=True, null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return "{}, {}, {}".format(self.id, self.created, self.error_type)


class BaseDateMetricsModel(TimeStampedModel):
    site = models.ForeignKey(Site, default=default_site)
    date_for = models.DateField()

    class Meta:
        abstract = True
        ordering = ['-date_for']

    @property
    def year(self):
        return self.date_for.year

    @property
    def month(self):
        return self.date_for.month


class SiteMauMetricsManager(models.Manager):
    """Custom model manager for SiteMauMMetrics model
    """
    def latest_for_site_month(self, site, year, month):
        """Return the latest record for the given site, month, and year
        If no record found, returns 'None'
        """
        queryset = self.filter(site=site, date_for__year=year, date_for__month=month)
        return queryset.order_by('-modified').first()  # pylint: disable=no-member


@python_2_unicode_compatible
class SiteMauMetrics(BaseDateMetricsModel):

    mau = models.IntegerField()
    objects = SiteMauMetricsManager()

    class Meta:
        unique_together = ('site', 'date_for',)

    @classmethod
    def save_metrics(cls, site, date_for, data, overwrite=False):
        """
        Convenience method to save metrics data with option to
        overwrite an existing record
        """
        if not overwrite:
            try:
                obj = SiteMauMetrics.objects.get(site=site, date_for=date_for)
                return (obj, False,)
            except SiteMauMetrics.DoesNotExist:
                pass

        return SiteMauMetrics.objects.update_or_create(site=site,
                                                       date_for=date_for,
                                                       defaults=dict(
                                                            mau=data['mau']))

    def __str__(self):
        return '{}, {}, {}, {}'.format(self.id,
                                       self.site.domain,
                                       self.date_for,
                                       self.mau)


class CourseMauMetricsManager(models.Manager):
    """Custom model manager for CourseMauMetrics model
    """
    def latest_for_course_month(self, site, course_id, year, month):
        """Return the latest record for the given site, course_id, month and year
        If no record found, returns 'None'
        """
        queryset = self.filter(
            site=site,
            course_id=course_id,
            date_for__year=year,
            date_for__month=month,
        )
        return queryset.order_by('-modified').first()  # pylint: disable=no-member


@python_2_unicode_compatible
class CourseMauMetrics(BaseDateMetricsModel):
    course_id = models.CharField(max_length=255)
    mau = models.IntegerField()
    objects = CourseMauMetricsManager()

    class Meta:
        unique_together = ('site', 'course_id', 'date_for',)

    @classmethod
    def save_metrics(cls, site, course_id, date_for, data, overwrite=False):
        """
        Convenience method to save metrics data with option to
        overwrite an existing record
        """
        if not overwrite:
            try:
                obj = CourseMauMetrics.objects.get(site=site,
                                                   course_id=course_id,
                                                   date_for=date_for)
                return (obj, False,)
            except CourseMauMetrics.DoesNotExist:
                pass

        return CourseMauMetrics.objects.update_or_create(site=site,
                                                         course_id=course_id,
                                                         date_for=date_for,
                                                         defaults=dict(
                                                            mau=data['mau']))

    def __str__(self):
        return '{}, {}, {}, {}, {}'.format(self.id,
                                           self.site.domain,
                                           self.course_id,
                                           self.date_for,
                                           self.mau)
