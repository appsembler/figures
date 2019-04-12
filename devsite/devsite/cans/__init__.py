"""
devsite.cans contains canned mock data to demo Figures

BE CAREFUL to avoid cyclical dependencies

"""

from .users import USER_DATA  # noqa
from .course_overviews import COURSE_OVERVIEW_DATA  # noqa
from .course_daily_metrics import COURSE_DAILY_METRICS_DATA  # noqa


COURSE_ACCESS_ROLE_DATA = [
    dict(
        username='wanda',
        org='StarFleetAcademy',
        course_id='course-v1:StarFleetAcademy+SFA01+2161',
        role='instructor'),
]
