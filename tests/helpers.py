'''Helper methods for Figures testing
'''

from dateutil.rrule import rrule, DAILY

import organizations


def make_course_key_str(org, number, run='test-run', **kwargs):
    '''
    Helper method to create a string representation of a CourseKey
    '''
    return 'course-v1:{}+{}+{}'.format(org, number, run)

def create_metrics_model_timeseries(factory, first_day, last_day):
    return [factory(date_for=dt) 
        for dt in rrule(DAILY, dtstart=first_day, until=last_day)]


def organizations_support_sites():
    """
    This function returns True if organizations supports site-organization
    mapping, False otherwise.

    This is used to conditionally run tests
    """
    orgs_has_site = hasattr(organizations.models.Organization, 'sites')
    return orgs_has_site
