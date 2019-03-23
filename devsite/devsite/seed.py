

import datetime
from dateutil.rrule import rrule, DAILY
import faker
import random

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db.utils import IntegrityError

from lms.djangoapps.certificates.models import GeneratedCertificate
from courseware.models import StudentModule
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField
from student.models import CourseAccessRole, CourseEnrollment, UserProfile

from figures.models import CourseDailyMetrics, SiteDailyMetrics
from figures.helpers import as_course_key, as_datetime, days_from, prev_day
from figures.pipeline import course_daily_metrics as pipeline_cdm
from figures.pipeline import site_daily_metrics as pipeline_sdm

from devsite import cans


DAYS_BACK = 180
LAST_DAY = prev_day(datetime.datetime.now())

FAKE = faker.Faker()


def get_site():
    """
    In demo mode, we have just one site (for now)
    """
    return Site.objects.first()


def days_back_list(days_back):
    end_date = prev_day(datetime.datetime.now())
    start_date = days_from(end_date, abs(days_back) * -1)
    return [day for day in rrule(DAILY, dtstart=start_date, until=end_date)]


def seed_course_overviews(data=None):

    if not data:
        data = cans.COURSE_OVERVIEW_DATA

    #import pdb; pdb.set_trace()
    for rec in data:
        course_id = rec['id']
        CourseOverview.objects.update_or_create(
            id=as_course_key(course_id),
            defaults=dict(
                display_name=rec['display_name'],
                org=rec['org'],
                display_org_with_default=rec['org'],
                number=rec['number'],
                created=rec['created'],
                enrollment_start=rec['enrollment_start'],
                enrollment_end=rec['enrollment_end'],
            )
        )


def clear_non_admin_users():
    '''
    '''
    users = get_user_model().objects.exclude(
        is_superuser=True).exclude(is_staff=True)
    users.delete()


def seed_users(data=None):
    '''
    '''
    if not data:
        data = cans.USER_DATA

    first_date = days_from(LAST_DAY, DAYS_BACK * -1)
    created_users = []
    for rec in data:
        try:
            profile_rec = rec.get('profile',None)
            user = get_user_model().objects.create_user(
                username=rec['username'],
                password=rec['password'],
                email=rec['email'],
                )
            user.is_staff = rec.get('is_staff', False)
            user.is_superuser = rec.get('is_superuser', False)
            user.date_joined = FAKE.date_between(first_date, LAST_DAY)
            user.save()
            created_users.append(user)
            if profile_rec:
                profile = UserProfile.objects.create(
                    user=user,
                    name=profile_rec['fullname'],
                    gender=profile_rec.get('gender',None),
                    country=profile_rec.get('country', None),
                )
        except IntegrityError as e:
            print('**** COLLISION **** {}'.format(e))
    return created_users


def seed_course_enrollments_for_course(course_id, users, max_days_back):
    '''

    '''
    today = datetime.datetime.now()

    def enroll_date(max_days_back):
        days_back = random.randint(1,abs(max_days_back))
        return days_from(today, days_back * -1 )

    for user in users:
        print('seeding course enrollment for user {}'.format(user.username))
        CourseEnrollment.objects.update_or_create(
            course_id=as_course_key(course_id),
            course_overview=CourseOverview.objects.get(id=course_id),
            user=user,
            created=enroll_date(max_days_back),
            )


def seed_course_enrollments():
    for co in CourseOverview.objects.all():
        #users_in_course = random.randint(40,200)
        users = seed_users(cans.users.UserGenerator(100))
        seed_course_enrollments_for_course(co.id, users, DAYS_BACK)


def seed_course_access_roles(data=None):
    if not data:
        data = cans.COURSE_TEAM_DATA

    for rec in data:
        #print('creating course access role')
        CourseAccessRole.objects.update_or_create(
            user=get_user_model().objects.get(username=rec['username']),
            org=rec['org'],
            course_id=as_course_key(rec['course_id']),
            role=rec['role'],
        )


def seed_student_modules():
    '''
    We're assuming active students here.
    Improvement is to skip a few and make others more active
    Do it in a normal distrubution
    '''

    for ce in CourseEnrollment.objects.all():
        for i in range(random.randint(1,5)):

            #sm_created = days_from(ce.created, random.randint(0,5))
            StudentModule.objects.update_or_create(
                student=ce.user,
                course_id=ce.course_id,
                created=ce.created,
                modified=FAKE.date_between(ce.created, LAST_DAY),
            )


def seed_course_completions():
    '''
    go over the dates
    '''
    end_date = LAST_DAY
    start_date = days_from(end_date, -180)


    for co in CourseOverview.objects.all():
        
        # Note there is a performance hit for using '?'
        qs = CourseEnrollment.objects.filter(course_id=co.id)
        # we just want a few of the enrollments to have completed

        # first cut, have 25% of learners complete course
        sample = int(qs.count() * 0.25)
        for ce in qs.order_by('?')[:sample]:
            GeneratedCertificate.objects.create(
                user=ce.user,
                course_id=co.id,
                created_date=FAKE.date_between(ce.created, LAST_DAY))


def seed_course_daily_metrics_fixed(data=None):
    if not data:
        data = cans.COURSE_DAILY_METRICS_DATA
    for index, rec in enumerate(data):
        print('seed CDM # {}'.format(index))
        CourseDailyMetrics.objects.update_or_create(
            course_id=rec['course_id'],
            date_for=rec['date_for'],
            defaults=dict(
                enrollment_count=rec['enrollment_count'],
                active_learners_today=rec['active_learners_today'],
                average_progress=rec['average_progress'],
                average_days_to_complete=rec['average_days_to_complete'],
                num_learners_completed=rec['num_learners_completed'],
            )
        )


def seed_course_daily_metrics_for_course(course_id):

    # get first date
    end_date = LAST_DAY
    start_date = days_from(end_date, -180)
    #extractor = pipeline_cdm.CourseDailyMetricsExtractor()

    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        #data = extractor.extract(course_id=course_id, date_for=dt,)
        # Hack data
        print('populating day {} for course {}'.format(dt, course_id))
        cdm, created = pipeline_cdm.CourseDailyMetricsLoader(course_id).load(
            date_for=dt, force_update=True)


def seed_course_daily_metrics():

    for co in CourseOverview.objects.all():
        print('seeding CDM for course {}'.format(co.id))
        seed_course_daily_metrics_for_course(co.id)


def seed_site_daily_metrics(data=None):
    '''
    Run seed_course_daily_metrics first

    Then, for each date for which we have a CDM record
    '''
    # for a_date in CourseDailyMetrics.objects.order_by('date_for').values_list(
    #     'date_for', flat=True).distinct():
    #     print('collecting for date {}'.format(a_date))

    end_date = LAST_DAY
    start_date = days_from(end_date, -180)
    #extractor = pipeline_cdm.CourseDailyMetricsExtractor()

    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        pipeline_sdm.SiteDailyMetricsLoader().load(site=get_site(),
            date_for=dt, force_update=True)


def wipe():
    clear_non_admin_users()
    CourseEnrollment.objects.all().delete()
    StudentModule.objects.all().delete()
    CourseOverview.objects.all().delete()
    CourseDailyMetrics.objects.all().delete()
    SiteDailyMetrics.objects.all().delete()


def seed_all():
    seed_course_overviews()
    seed_users()
    seed_course_enrollments()
    # Need to fix this one
    #seed_course_access_roles()
    seed_student_modules()
    seed_course_completions()
    seed_course_daily_metrics()
    seed_site_daily_metrics()
