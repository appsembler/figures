"""Defines Figures models

TODO: Create a base "SiteModel" or a "SiteModelMixin"
"""

from __future__ import absolute_import
from datetime import date
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F
from django.utils.encoding import python_2_unicode_compatible

from jsonfield import JSONField

from model_utils.models import TimeStampedModel

from figures.compat import CourseEnrollment
from figures.helpers import as_course_key
from figures.progress import EnrollmentProgress


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
    # TODO: Review the most appropriate on_delete behaviour
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    date_for = models.DateField(db_index=True)

    # Leaving as a simple string for initial development
    # TODO: Follow on to decide if we want to make this an FK to
    # the CourseOverview model or have the course_id be a
    # CourseKeyField
    course_id = models.CharField(max_length=255, db_index=True)
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

    # As of Figures 0.3.13, this is the total number of certificates granted
    # for the course as of the "date_for"
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

    When we upgrade to MAU 2G, we'll add a new field, 'active_users_today'
    and pull the data from the previous day's live active user capture
    """
    # TODO: Review the most appropriate on_delete behaviour
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    # Date for which this record's data are collected
    date_for = models.DateField(db_index=True)

    # Under review for deletion
    cumulative_active_user_count = models.IntegerField(blank=True, null=True)

    todays_active_user_count = models.IntegerField(blank=True, null=True)
    total_user_count = models.IntegerField()
    course_count = models.IntegerField()
    total_enrollment_count = models.IntegerField()

    # Should change this to default value of 0
    mau = models.IntegerField(blank=True, null=True)

    # TODO: Add field for number of CDMs reported

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
        recs = cls.objects.filter(**filter_args).order_by('-date_for')
        return recs[0] if recs else None


@python_2_unicode_compatible
class SiteMonthlyMetrics(TimeStampedModel):
    """
    Stores metrics for a given site and month


    """
    # TODO: Review the most appropriate on_delete behaviour
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
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


class EnrollmentDataManager(models.Manager):
    """Custom model manager for EnrollmentData

    Initial purpose is to handle the logic of creating and updating
    EnrollmentData instances.

    """
    def set_enrollment_data(self, site, user, course_id, course_enrollment=False):
        """
        This is an expensive call as it needs to call CourseGradeFactory if
        there is not already a LearnerCourseGradeMetrics record for the learner
        """
        if not course_enrollment:
            # For now, let it raise a `CourseEnrollment.DoesNotExist
            # Later on we can add a try block and raise out own custom
            # exception
            course_enrollment = CourseEnrollment.objects.get(
                user=user,
                course_id=as_course_key(course_id))

        defaults = dict(
            is_enrolled=course_enrollment.is_active,
            date_enrolled=course_enrollment.created,
        )

        # Note: doesn't use site for filtering
        lcgm = LearnerCourseGradeMetrics.objects.latest_lcgm(
            user=user,
            course_id=str(course_id))
        if lcgm:
            # do we already have an enrollment data record
            # We may change this to use
            progress_data = dict(
                date_for=lcgm.date_for,
                is_completed=lcgm.completed,
                progress_percent=lcgm.progress_percent,
                points_possible=lcgm.points_possible,
                points_earned=lcgm.points_earned,
                sections_possible=lcgm.sections_possible,
                sections_worked=lcgm.sections_worked
            )
        else:
            ep = EnrollmentProgress(user=user, course_id=course_id)
            # TODO: If we get progress worked and there is no LCGM, then we have
            # a bug OR there was progress after the last daily metrics collection
            progress_data = dict(
                date_for=date.today(),
                is_completed=ep.is_completed(),
                progress_percent=ep.progress_percent(),
                points_possible=ep.progress.get('points_possible', 0),
                points_earned=ep.progress.get('points_earned', 0),
                sections_possible=ep.progress.get('sections_possible', 0),
                sections_worked=ep.progress.get('sections_worked', 0)
            )
        defaults.update(progress_data)

        obj, created = self.update_or_create(
            site=site,
            user=user,
            course_id=str(course_id),
            defaults=defaults)
        return obj, created


@python_2_unicode_compatible
class EnrollmentData(TimeStampedModel):
    """Tracks most recent enrollment data for an enrollment

    An enrollment is a unique site + user + course

    This model stores basic enrollment information and latest progress
    The purpose of this class is for query performance for the 'learner-metrics'
    API endpoint which is needed for the learner progress overview page.

    This is an intial take on caching current enrollment data with the dual
    purposes of speeding up the learner-metrics endpoint needed for the LPO page
    as well as doing so in clear maintainable code.

    At some point in the future, we'll probably have to construct a key-value
    high performance storage, but for now, we'd like to see how far we can get
    with the basic Django architecture. Plus this simplifies running Figures on
    small Open edX LMS deployments
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    course_id = models.CharField(max_length=255, db_index=True)
    date_for = models.DateField(db_index=True)

    # Date enrolled is from CourseEnrollment.created
    date_enrolled = models.DateField(db_index=True)

    # From CourseEnrollment.is_active
    is_enrolled = models.BooleanField()

    # From LCGM.completed property methods
    is_completed = models.BooleanField()
    progress_percent = models.FloatField(default=0.00)

    # from LCGM fields
    points_possible = models.FloatField()
    points_earned = models.FloatField()
    sections_worked = models.IntegerField()
    sections_possible = models.IntegerField()

    objects = EnrollmentDataManager()

    class Meta:
        unique_together = ('site', 'user', 'course_id')

    def __str__(self):
        return '{} {} {} {}'.format(
            self.id, self.site.domain, self.user.email, self.course_id)

    @property
    def progress_details(self):
        """This method gets the progress details
        This method is a temporary fix until the serializers are updated.
        """
        return dict(
            points_possible=self.points_possible,
            points_earned=self.points_earned,
            sections_worked=self.sections_worked,
            sections_possible=self.sections_possible,
        )


class LearnerCourseGradeMetricsManager(models.Manager):
    """Custom model manager for LearnerCourseGrades model
    """
    def latest_lcgm(self, user, course_id):
        """Gets the most recent record for the given user and course

        We have this because we implement sparse data, meaning we only create
        new records when data has changed. this means that for a given course,
        learners may not have the same "most recent date"

        This means we have to be careful of where we use this method in our
        API as it costs a query per call. We will likely require restructuring
        or augmenting our data if we need to bulk retrieve

        TODO: Consider if we want to add 'site' as a parameter and update the
        uniqueness constraint to be: site, course_id, user, date_for
        """
        queryset = self.filter(user=user,
                               course_id=str(course_id)).order_by('-date_for')
        return queryset[0] if queryset else None

    def most_recent_for_course(self, course_id):
        statement = """ \
        SELECT id, user_id, course_id, MAX(date_for)
        FROM figures_learnercoursegrademetrics lcgm
        WHERE course_id = {course_id} AND
        GROUP BY user_id, course_id
        """
        return self.raw(statement.format(course_id=str(course_id)))

    def completed_for_site(self, site, **_kwargs):
        """Return course_id/user_id pairs that have completed
        Initial filters on list of users, listr of course ids

        User IDs can be filtered by passing `user_id=` list of user ids

        Course IDs can be filtered by passing `course_ids=` list of course ids

        Returns a distinct QuerySet dict list of values with keys
        'course_id' and 'user_id'

        We will consider adding a "completed" field to the model for faster
        filtering, since we can index on the field. However, we need to evaluate
        the additional storage need
        """
        qs = self.filter(site=site,
                         sections_possible__gt=0,
                         sections_worked=F('sections_possible'))

        # Build out filter. Note, we don't check if the var is iterable
        # we let it fail of invalid values passed in
        filter_args = dict()
        user_ids = _kwargs.get('user_ids', None)
        if user_ids:
            filter_args['user_id__in'] = user_ids
        course_ids = _kwargs.get('course_ids', None)
        if course_ids:
            # We do the string casting in case couse_ids are CourseKey instance
            filter_args['course_id__in'] = [str(key) for key in course_ids]
        if filter_args:
            qs = qs.filter(**filter_args)
        return qs

    def completed_ids_for_site(self, site, **_kwargs):
        qs = self.completed_for_site(site, **_kwargs)
        return qs.values('course_id', 'user_id').distinct()

    def completed_raw_for_site(self, site, **_kwargs):
        """Experimental
        """
        statement = """ \
        SELECT id, user_id, course_id, MAX(date_for)
        FROM figures_learnercoursegrademetrics lcgm
        WHERE site_id = {site} AND
        lcgm.sections_possible > 0 AND
        lcgm.sections_worked = lcgm.sections_possible
        GROUP BY user_id, course_id
        ORDER BY user_id, course_id
        """
        return self.raw(statement.format(site=site))


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
    Reason is we're likely more interested in the learner and the course than
    the specific course enrollment. Also means that the Figures models do not
    have a hard dependency on models in edx-platform

    Considered using DecimalField for points as we can control the decimal places
    But for now, using float, as I'm not entirely sure how many decimal places are
    actually needed and edx-platform uses FloatField in its grades models


    TODO: Add fields
        `is_active` - get the 'is_active' value from the enrollment at the time
        this record is created
        `completed` - This lets us filter on a table column instead of
                      calculating it
    TODO: Add index on 'course_id', 'date_for', 'completed'
    """
    # TODO: Review the most appropriate on_delete behaviour
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    date_for = models.DateField(db_index=True)
    # TODO: We should require the user
    # TODO: Review the most appropriate on_delete behaviour
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             blank=True,
                             null=True,
                             on_delete=models.CASCADE)
    course_id = models.CharField(max_length=255, blank=True, db_index=True)
    points_possible = models.FloatField()
    points_earned = models.FloatField()
    sections_worked = models.IntegerField()
    sections_possible = models.IntegerField()

    objects = LearnerCourseGradeMetricsManager()

    class Meta:
        """
        Do we want to add 'site' to the `unique_together` set?
        Open edX Course IDs are globally unique, so it is not required
        """
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

    @property
    def completed(self):
        return (self.sections_worked > 0 and
                self.sections_worked == self.sections_possible)


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
    # TODO: Review the most appropriate on_delete behaviour
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             blank=True,
                             null=True,
                             on_delete=models.CASCADE)
    site = models.ForeignKey(Site, blank=True,
                             null=True,
                             on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return "{}, {}, {}".format(self.id, self.created, self.error_type)


class BaseDateMetricsModel(TimeStampedModel):
    # TODO: Review the most appropriate on_delete behaviour
    site = models.ForeignKey(Site, default=default_site, on_delete=models.CASCADE)
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
        queryset = self.filter(site=site,
                               date_for__year=year,
                               date_for__month=month)
        return queryset.order_by('-modified').first()


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
        return queryset.order_by('-modified').first()


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
