

import datetime
from dateutil.rrule import rrule, DAILY

from random import randint, random

from figures.helpers import days_from, prev_day

from .course_overviews import COURSE_OVERVIEW_DATA


def gen_avg_progress(prev_days_value):
    '''
    Implement a reasonable range based on previous day's values
    '''
    return float('{0:.2f}'.format(random()))

def gen_num_learners_completed(yesterday):
    prev_val = yesterday.get('num_learners_completed',0)
    enrollment_count = yesterday.get('enrollment_count', 0)
    max_possible = max(0, enrollment_count - prev_val)
    todays_val = randint(0, max_possible)
    return prev_val + todays_val


def generate_cdm_data_for_course(course_id):
    '''
    Just getting it working first, then we'll make the values more reasonable

    like value = sorted([lower_bound, x, upper_bound])[1]

    '''
    cdm_data = []
    yesterday = {}
    end_date = prev_day(datetime.datetime.now())
    start_date = days_from(end_date, -180)

    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        enrollment_count = yesterday.get('enrollment_count',0) + randint(0,10)
        average_progress = gen_avg_progress(yesterday.get('average_progress', 0))
        average_days_to_complete = randint(10,30)
        num_learners_completed = gen_num_learners_completed(yesterday)

        rec = dict(
            course_id=course_id,
            date_for=dt.strftime('%Y-%m-%d'),
            enrollment_count=enrollment_count,
            active_learners_today=randint(0, enrollment_count /2),
            average_progress=average_progress,
            average_days_to_complete=average_days_to_complete,
            num_learners_completed=num_learners_completed,
        )
        cdm_data.append(rec)
        yesterday = rec
    return cdm_data


COURSE_DAILY_METRICS_DATA = [
    a for b in 
        [generate_cdm_data_for_course(rec['id']) for rec in COURSE_OVERVIEW_DATA]
        for a in b
]
