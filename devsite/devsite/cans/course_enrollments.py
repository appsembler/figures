'''
First cut, we're just populating a single course
'''

from student.models import CourseEnrollment

from .course_overviews import COURSE_OVERVIEW_DATA
from .users import FIXED_USER_DATA


def generate_course_enrollments():
    ce = []

    dates = ['2018-08-01', '2018-09-01', '2018-10-1', '2018-10-1']
    for i, d in enumerate(dates):
        ce.append(
            dict(
                course_id=COURSE_OVERVIEW_DATA[0]['id'],
                username=FIXED_USER_DATA[i]['username'],
                created=d,
            ),
        )
    return ce


COURSE_ENROLLMENT_DATA = generate_course_enrollments()



def seed_course_enrollments_fixed(data=None):
    '''Use this

    '''
    if not data:
        data = cans.COURSE_ENROLLMENT_DATA

    for rec in data:
        course_id = as_course_key(rec['course_id'])
        print('seeding course enrollment for user {}'.format(rec['username']))
        CourseEnrollment.objects.update_or_create(
            course_id=course_id,
            course_overview=CourseOverview.objects.get(id=course_id),
            user=get_user_model().objects.get(username=rec['username']),
            created=as_datetime(rec['created']),
            )
