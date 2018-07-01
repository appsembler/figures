
import datetime
from dateutil.rrule import rrule
from dateutil.relativedata import relativedata

from figures.helpers import prev_day
from figures.models import CourseDailyMetrics, SiteDailyMetrics

'''

We're starting with doing monthly metrics. Then we will refactor to provide
programmatic timespans
'''

def current_month_time_frame():
    '''
    
    '''
    today = datetime.datetime.now()
    start_of_month = datetime.date(today.year, today.month, 1)
    end_of_month = None



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






def get_monthly_site_metrics():
    '''Gets current metrics with history
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
    last_day = prev_day(datetime.datetime)


    # get the start and end dates for the periods

    current_monthly_active_users = 400
    active_user_history = [
    ]
    total_site_user_history = [
    ]
    
    return dict(
        monthly_active_users=dict(
            current=current_monthly_active_users,
            history=active_user_history,
            ),
        total_site_users=dict(
            current=current_total_site_users,
            history=total_site_user_history,
            )

    )

    '''
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
    '''

