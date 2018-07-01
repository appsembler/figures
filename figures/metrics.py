
from collections import namedtuple

import datetime
from dateutil.rrule import rrule
from dateutil.relativedelta import relativedelta

from courseware.models import StudentModule

from figures.helpers import (
    next_day,
    prev_day,
    previous_months_iterator,
    )
from figures.models import CourseDailyMetrics, SiteDailyMetrics




'''

We're starting with doing monthly metrics. Then we will refactor to provide
programmatic timespans
'''

def current_month_time_frame():
    '''
    
    '''
    today = datetime.datetime.now()
    return datetime.date(today.year, today.month, 1), today

# def make_time_series():
#     '''
#     we want to return 
#     '''
#     for dt in rrule()


def daily_metrics_for_month(date_for, metrics_model, include_today=False):
    '''
    retrieve all metrics for the year and month in the given date
    If the month is the current month get all available days for the month
    not including today unless ``include_today`` is True

    TODO: Make this a model manager method
    '''
    today = datetime.datetime.now()
    if today.year == date_for.year and today.month == date_for.month:
        return metrics_model.objects.filter(
            date_for__gte=datetime.date(today.year, today.month, 1)).filter(
            date_for__lt=today.date())

    else:
        return metrics_model.objects.filter(date_for__year=date_for.year,
            date_for__month=date_for.month)



def active_users_for_time_period(start_date, end_date, site=None, course_ids=None):

    filter_args = dict(
        created__gt=prev_day(start_date),
        modified__lt=next_day(end_date)
        )
    if course_ids:
        filter_args['course_ids__in']=course_ids

    # TODO: In test
    return StudentModule.objects.filter(**filter_args).values('student__id').distinct().count()


def period_str(month_tuple):
    #import pdb; pdb.set_trace()
    return datetime.date(*month_tuple).strftime('%B, %Y')

def get_monthly_active_users(today, months_back=6):

    # current_monthly_active_users = active_users_for_time_period(
    #     start_date=this_month.start_of_month,
    #     end_date=yesterday)

    if isinstance(today, datetime.datetime):
        today=today.date()

    assert isinstance(today, datetime.date), (
            'today cannot be of type {}. It must be a datetime.datetime or datetime.date'.format(
                type(today))
        )
    current_month = StudentModule.objects.filter(
        created__gt=prev_day(datetime.date(year=today.year, month=today.month, day=1)),
        modified__lt=today,
        ).values('student__id').distinct().count()

    history=[]

    for month in previous_months_iterator(month_for=today, months_back=months_back,):
        period=period_str(month)
        value=active_users_for_time_period(
                start_date=datetime.date(month[0], month[1],1),
                end_date=datetime.date(month[0],month[1], month[2]))
        history.append(dict(
            period=period,
            value=value,
            )
        )

    return dict(
        current_month=current_month,
        history=history,
    )

def get_monthly_site_metrics(today=None):
    '''Gets current metrics with history

    Arg: today - if specified, uses that date as the 'current' date
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
    today = datetime.datetime.now()
    yesterday = prev_day(today)

    months_back=6

    ##
    ## Brute force this.
    ##

    monthly_active_users = get_monthly_active_users(
        today=today, months_back=months_back)


    total_site_users = None
    total_site_coures = None
    total_course_enrollments = None
    total_course_completions = None

    ## Then, we can put the method calls into a dict, load the dict from
    ## settings

    total_site_user_history = [
    ]
    
    return dict(
        monthly_active_users=monthly_active_users,
        total_site_users=total_site_users,
        total_site_coures=total_site_coures,
        total_course_enrollments=total_course_enrollments,
        total_course_completions=total_course_completions,
    )


def test(today=None):
    if not today:
        today = datetime.datetime.now().date()
    print('testing with date: {}'.format(today))
    vals = get_monthly_site_metrics(today)
    from pprint import pprint
    pprint(vals)
