'''

We're starting with doing monthly metrics. Then we will refactor to provide
programmatic timespans

Design note:
prefer querying metrics models (if the data are available there) over querying
edx-platform models with the exception of CourseOverview


NOTE: We're starting to grow this module enough that we want to
* refactor into a module directory
* create separate metrics submodule files for functional areas
* Add public facing submodule object and function declarations to metrics/__init__.py

Security note: This module does NOT perform user authorization. THEREFORE make
sure that any code that calls these methods is properly authorizing the user

After initial production release, We will follow on with adding 'site' as a
parameter to support multi-tenancy

'''

from collections import namedtuple

import datetime

from dateutil.parser import parse as dateutil_parse
from dateutil.rrule import rrule
from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from django.db.models import Max

from certificates.models import GeneratedCertificate
from courseware.courses import get_course_by_id
from courseware.models import StudentModule
from lms.djangoapps.grades.new.course_grade_factory import CourseGradeFactory
from student.models import CourseEnrollment

from figures.helpers import (
    as_course_key,
    next_day,
    prev_day,
    previous_months_iterator,
    )
from figures.models import CourseDailyMetrics, SiteDailyMetrics


##
## Helpers (consider moving to the ``helpers`` module
##

def period_str(month_tuple):
    '''Returns display date for the given month tuple containing year, month, day
    '''
    return datetime.date(*month_tuple).strftime('%B, %Y')

def cast_to_date(val):
    if isinstance(val, datetime.date):
        return val
    elif isinstance(val, datetime.datetime):
        return val.date()
    elif isinstance(val, basestring):
        return dateutil_parse(val).date()
    else:
        raise Exception('date cannot be of type {}. It must be able to be cast to a datetime.date'.format(
            val))


##
## Learner specific data/metrics
##

class LearnerCourseGrades(object):
    '''
    TODO: create lazy method to get the CourseOverview object

    Members
    self.course: xblock.internal.CourseDescriptorWithMixins
    self.course_grade: lms.djangoapps.grades.new.course_grade.CourseGrade

    course_grade.chapter_grades is an OrderedDict of
    keys:
        BlockUsageLocator(CourseLocator(u'edX', u'DemoX', u'Demo_Course', None, None)
    values:

    TODO: Make convenience method to instantiate from a GeneratedCertificate
    '''
    def __init__(self, user_id, course_id):
        '''
        Tidbits:
        courseware_summary = course_grade.chapter_grades.values()
        grade_summary = course_grade.summary

        '''
        self.learner = get_user_model().objects.get(id=user_id)
        self.course = get_course_by_id(course_key=as_course_key(course_id))
        self.course._field_data_cache = {}  # pylint: disable=protected-access
        self.course.set_grading_policy(self.course.grading_policy)
        self.course_grade = CourseGradeFactory().create(self.learner, self.course)

    def __str__(self):
        return u'{} - {} - {} '.format(
            self.course.id, self.learner.id, self.learner.username)

    @property
    def chapter_grades(self):
        '''convenience wrapper, mostly as a reminder'''
        return self.course_grade.chapter_grades

    def certificates(self):
        return GeneratedCertificate.objects.filter(
            user=self.learner).filter(course_id=self.course.id).count()

    def learner_completed(self):
        pass

    def is_section_graded(self, section):
        # just being defensive, might not need to check if
        # all_total exists and if all_total.possible exists
        if (hasattr(section, 'all_total') and hasattr(section.all_total, 'possible') and section.all_total.possible > 0):
            return True
        else:
            return False

    def sections(self, only_graded=False, **kwargs):
        '''
        yields objects of type:
        lms.djangoapps.grades.new.subsection_grade.SubsectionGrade
        '''

        for chapter_grade in self.course_grade.chapter_grades.values():
            for section in chapter_grade['sections']:
                if not only_graded or (only_graded and self.is_section_graded(section)):
                    yield section


    def sections_list(self, only_graded=False):
        '''
        Convenience method that returns a list by calling the iterator method,
        ``sections``
        '''
        # sections = []
        # sections += [chapter_grade['sections'] for chapter_grade in self.chapter_grades.values()]
        # return sections

        #return [sec for sec in cg['sections'] for cg in self.chapter_grades.values()]
        #vals = self.chapter_grades.values()

        #return [item for sublist in vals for item in sublist['sections']]

        #return [item for sublist in self.chapter_grades.values() for item in sublist['sections']]

        return [section for section in self.sections(only_graded=only_graded)]

    # def graded_sections(self):
    #     '''Convenience wrapper'''
    #     return sections_list(only_graded=true)

    # def progress_metric_a(self):
    #     '''
        
    #     '''
    #     count = earned = 0

    #     for section in self.sections(only_graded=True):
    #         if section.all_total.earned > 0:
    #             earned += 1
    #         count += 1

    #     return dict(count=count, 
    #         earned=earned,
    #         sections=self.sections_list(only_graded=True))


    def progress(self):
        count = possible = earned = 0

        for section in self.sections(only_graded=True):
            if section.all_total.earned > 0:
                earned += 1
            count += 1
            possible += section.all_total.possible

        return dict(
            possible=possible,
            earned=earned,
            count=count)

    def progress_percent(self, progress_details=None):
        '''
        TODO: This func needs work
        '''
        if not progress_details:
            progress_details = self.progress()
        if progress_details.get('possible'):
            return float(progress_details['earned'])/float(progress_details['possible'])
        else:
            return 0.0

    def print_subsection(self):
        for section in self.sections(only_graded=True):
            print('display_name: {}'.format(section.display_name))
            print('due: {}'.format(section.due))
            print('subtree_edited_timestamp: {}'.format(section.subtree_edited_timestamp))


class LearnerCourseProgress(object):
    '''
    TODO:
    * Need to add tests
    '''
    def __init__(self, user_id, course_id):
        self.user_id = user_id
        self.course_id = course_id
        self.student_modules = StudentModule.objects.filter(
            student_id=user_id,
            course_id=as_course_key(course_id))

    def get_progress_for_time_period(start_date, end_date):
        filter_args = dict(
            created__gt=prev_day(start_date),
            modified__lt=next_day(end_date)
            )
        sm = self.student_modules.filter(**filter_args)

        progress = 0.0
        return progress

    def get_previous_progress(months_back=3):
        date_for = datetime.datetime.today().date()
        history = []
        for month in previous_months_iterator(month_for=date_for, months_back=months_back,):
            period=period_str(month)
            value=self.get_progress_for_time_period(
                start_date=datetime.date(month[0], month[1],1),
                end_date=datetime.date(month[0],month[1], month[2]))
            history.append(dict(period=period,value=value))
        return history


##
## Support methods for Course and Sitewide aggregate metrics
##
## Note the common theme in many of these methods in filtering on a date range
## Also note that some methods have two inner methods. One to retrieve raw data
## from the original model, the other to retrieve from the Figures metrics model
## The purpose of this is to be able to switch back and forth in development
## The metrics model may not be populated in devstack, but we want to exercize 
## the code. 
## Retrieving from the Figures metrics models should be much faster
##
## We may refactor these into a base class with the contructor params of
## start_date, end_date, site

def get_active_users_for_time_period(start_date, end_date, site=None, course_ids=None):

    filter_args = dict(
        created__gt=prev_day(start_date),
        modified__lt=next_day(end_date)
        )
    if course_ids:
        filter_args['course_ids__in']=course_ids

    return StudentModule.objects.filter(**filter_args).values('student__id').distinct().count()


def get_total_site_users_for_time_period(start_date, end_date, site=None, **kwargs):

    def calc_from_user_model():
        filter_args = dict(
            date_joined__lt=next_day(end_date),
        )
        return get_user_model().objects.filter(**filter_args).count()

    def calc_from_site_daily_metrics():
        filter_args = dict(
            date_for__gt=prev_day(start_date),
            date_for__lt=next_day(end_date),
        )
        qs = SiteDailyMetrics.objects.filter(**filter_args)
        if qs:
            return qs.aggregate(maxval=Max('total_user_count'))['maxval']
        else:
            return 0

    return calc_from_site_daily_metrics()


def get_total_site_users_joined_for_time_period(start_date, end_date, site=None, course_ids=None):
    '''returns the number of new enrollments for the time period

    NOTE: Untested and not yet used in the general site metrics, but we'll want to add it

    '''
    def calc_from_user_model():
        filter_args = dict(
            date_joined__gt=prev_day(start_date),
            date_joined__lt=next_day(end_date),
            )
        return get_user_model().objects.filter(**filter_args).values('id').distinct().count()

    return calc_from_user_model()


def get_total_enrolled_users_for_time_period(start_date, end_date, site=None, course_ids=None):
    '''
    
    '''
    filter_args = dict(
        date_for__gt=prev_day(start_date),
        date_for__lt=next_day(end_date),
        )

    qs = SiteDailyMetrics.objects.filter(**filter_args)
    if qs:
        return qs.aggregate(maxval=Max('total_enrollment_count'))['maxval']
    else:
        return 0


def get_total_site_courses_for_time_period(start_date, end_date, site=None, course_ids=None):
    '''
    Potential fix:
    get unique course ids from CourseEnrollment
    '''
    def calc_from_site_daily_metrics():
        filter_args = dict(
            date_for__gt=prev_day(start_date),
            date_for__lt=next_day(end_date),
        )
        qs = SiteDailyMetrics.objects.filter(**filter_args)
        if qs:
            return qs.aggregate(maxval=Max('course_count'))['maxval']
        else:
            return 0

    def calc_from_course_enrollments():
        filter_args = dict(
            created__gt=prev_day(start_date),
            created__lt=next_day(end_date),
            )
        return CourseEnrollment.objects.filter(
            **filter_args).values('course_id').distinct().count()

    return calc_from_course_enrollments()


def get_total_course_completions_for_time_period(start_date, end_date, site=None, course_ids=None):
    '''
    This metric is not currently captured in SiteDailyMetrics, so retrieving from
    course dailies instead
    '''
    def calc_from_course_daily_metrics():
        filter_args = dict(
            date_for__gt=prev_day(start_date),
            date_for__lt=next_day(end_date),
        )
        qs = CourseDailyMetrics.objects.filter(**filter_args)
        if qs:
            return qs.aggregate(maxval=Max('num_learners_completed'))['maxval']
        else:
            return 0

    return calc_from_course_daily_metrics()


def get_monthly_history_metric(func,date_for, months_back):
    date_for = cast_to_date(date_for)
    history = []

    for month in previous_months_iterator(month_for=date_for, months_back=months_back,):
        period=period_str(month)
        value=func(
                start_date=datetime.date(month[0], month[1],1),
                end_date=datetime.date(month[0],month[1], month[2]),
        )
        history.append(dict(period=period, value=value,))
    current_month = history.pop()
    return dict(
        current_month=current_month['value'],
        history=history,)


# TODO make 'cast_to_date' a decorator on the 'date_for' param
# - Do the same for all these get methods
# TODO: Generalize the 'get_some_metric_x' methods below,
# the only significant different is the value called for each time period (month)

def get_monthly_active_users(date_for, months_back):

    date_for = cast_to_date(date_for)

    history=[]

    for month in previous_months_iterator(month_for=date_for, months_back=months_back,):
        period=period_str(month)
        value=get_active_users_for_time_period(
                start_date=datetime.date(month[0], month[1],1),
                end_date=datetime.date(month[0],month[1], month[2]))
        history.append(dict(
            period=period,
            value=value,
            )
        )
    current_month = history.pop()
    return dict(
        current_month=current_month['value'],
        history=history,
    )


def get_monthly_site_metrics(date_for=None, **kwargs):
    '''Gets current metrics with history

    Arg: date_for - if specified, uses that date as the 'current' date
    Useful for testing and for looking at past days as 'today'
    TODO: Add site filter for multi-tenancy

    {
      "monthly_active_users": {
        "current_month": 1323,
        "history": [
          {
            "period": "April 2018 (best to be some standardised Date format that I can parse)",
            "value": 1022,
          },
          {
            "period": "March 2018",
            "value": 1022,
          },
          ...
        ]
      },
      "total_site_users": {
        // represents total number of registered users for org/site
        "current": 4931,
        "history": [
          {
            "period": "April 2018",
            "value": 4899,
          },
          ...
        ]
      },
      "total_site_courses": {
        "current": 19,
        "history": [
          {
            "period": "April 2018",
            "value": 17,
          },
          ...
        ]
      },
      "total_course_enrollments": {
        // sum of number of users enrolled in all courses
        "current": 7911,
        "history": [
          {
            "period": "April 2018",
            "value": 5911,
          },
          ...
        ]
      },
      "total_course_completions": {
        // number of times user has completed a course in this month
        "current": 129,
        "history": [
          {
            "period": "April 2018",
            "value": 101,
          },
          ...
        ]
      }
    }
    '''

    if date_for:
        date_for = cast_to_date(date_for)
    else:
        date_for = datetime.datetime.now().date()

    months_back=kwargs.get('months_back', 6) # Warning: magic number

    ##
    ## Brute force this for now. Later, refactor to define getters externally,
    ## and rely more on the serializers to stitch data together to respond
    ##
    ## Then, we can put the method calls into a dict, load the dict from
    ## settings, for example, or a Django model

    # We are retrieving data here in series before constructing the return dict
    # This makes it easier to inspect
    monthly_active_users = get_monthly_active_users(
        date_for=date_for, months_back=months_back)

    total_site_users = get_monthly_history_metric(
        func=get_total_site_users_for_time_period,
        date_for=date_for,
        months_back=months_back,
        )
    total_site_coures = get_monthly_history_metric(
        func=get_total_site_courses_for_time_period,
        date_for=date_for,
        months_back=months_back,
        )
    total_course_enrollments = get_monthly_history_metric(
        func=get_total_enrolled_users_for_time_period,
        date_for=date_for,
        months_back=months_back,
        )
    total_course_completions = get_monthly_history_metric(
        func=get_total_course_completions_for_time_period,
        date_for=date_for,
        months_back=months_back,
        )

    return dict(
        monthly_active_users=monthly_active_users,
        total_site_users=total_site_users,
        total_site_coures=total_site_coures,
        total_course_enrollments=total_course_enrollments,
        total_course_completions=total_course_completions,
    )


# Convenience for the REPL

def test(date_for=None):
    if not date_for:
        date_for = datetime.datetime.now().date()
    print('testing with date: {}'.format(date_for))
    vals = get_monthly_site_metrics(date_for)
    from pprint import pprint
    pprint(vals)
    return vals
