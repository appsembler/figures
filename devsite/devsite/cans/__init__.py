'''
devsite.cans contains canned mock data to demo Figures

BE CAREFUL to avoid cyclical dependencies

'''

from .users import USER_DATA
from .course_overviews import COURSE_OVERVIEW_DATA
from .course_enrollments import COURSE_ENROLLMENT_DATA
from .student_modules import STUDENT_MODULE_DATA
from .course_daily_metrics import COURSE_DAILY_METRICS_DATA
from .site_daily_metrics import SITE_DAILY_METRICS_DATA


COURSE_ACCESS_ROLE_DATA = [
    dict(
        username='wanda',
        org='StarFleetAcademy',
        course_id='course-v1:StarFleetAcademy+SFA01+2161',
        role='instructor'),
]
