"""
Fills the standalone development environment database

* First populates platform mock models then populates figures metrics from the
  mock platform data
"""

from __future__ import absolute_import
from __future__ import print_function
import datetime
from dateutil.rrule import rrule, DAILY
import faker
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db.utils import IntegrityError
from django.utils.timezone import utc

from figures.compat import StudentModule

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from student.models import CourseAccessRole, CourseEnrollment, UserProfile

from organizations.models import Organization, OrganizationCourse

from figures.backfill import backfill_enrollment_data_for_site
from figures.compat import RELEASE_LINE, GeneratedCertificate
from figures.models import (
    CourseDailyMetrics,
    EnrollmentData,
    LearnerCourseGradeMetrics,
    SiteDailyMetrics,
    SiteMonthlyMetrics,
)
from figures.helpers import (
    as_course_key,
    as_datetime,
    days_from,
    prev_day,
    is_multisite,
)
from figures.pipeline import course_daily_metrics as pipeline_cdm
from figures.pipeline import site_daily_metrics as pipeline_sdm
from figures.sites import get_organizations_for_site, get_sites

from devsite import cans
from six.moves import range

if is_multisite():
    # First trying this without capturing 'ImportError'
    from organizations.models import UserOrganizationMapping


FAKE = faker.Faker()
LAST_DAY = days_from(datetime.datetime.now(), -2).replace(tzinfo=utc)


DAYS_BACK = settings.DEVSITE_SEED['DAYS_BACK']
NUM_LEARNERS_PER_COURSE = settings.DEVSITE_SEED['NUM_LEARNERS_PER_COURSE']

# Quick and dirty debuging
VERBOSE = False


FOO_ORG = 'FOO'


def get_site():
    """
    In demo mode, we have just one site (for now)
    """
    return Site.objects.first()


def today():
    return datetime.datetime.utcnow().date()


def days_back_list(days_back):
    end_date = prev_day(datetime.datetime.now())
    start_date = days_from(end_date, abs(days_back) * -1)
    return [day for day in rrule(DAILY, dtstart=start_date, until=end_date)]


def generate_course_overview(index, **vals):

    org = vals.get('org', 'ORG-{}'.format(index))

    rec = dict(
        # id='course-v1:StarFleetAcademy+SFA01+2161',
        display_name=vals.get('display_name', FAKE.sentence(nb_words=2)),
        org=org,
        display_org_with_default=org,
        number=vals.get('number', 'NUM-{}'.format(index)),
        created='2018-07-01',
        enrollment_start='2018-08-01',
        enrollment_end='2018-12-31',
        )
    run = '000{}'.format(index)
    rec['id'] = 'course-v1:{0}+{1}+{2}'.format(org, rec['number'], run)
    return rec


def seed_course_overviews(data=None):

    if not data:
        data = cans.COURSE_OVERVIEW_DATA
        # append with randomly generated course overviews to test pagination
        new_courses = [generate_course_overview(i, org=FOO_ORG) for i in range(20)]
        data += new_courses

    for rec in data:
        course_id = rec['id']
        defaults = dict(
                display_name=rec['display_name'],
                org=rec['org'],
                display_org_with_default=rec['org'],
                number=rec['number'],
                created=as_datetime(rec['created']).replace(tzinfo=utc),
                start=as_datetime(rec['enrollment_start']).replace(tzinfo=utc),
                end=as_datetime(rec['enrollment_end']).replace(tzinfo=utc),
                enrollment_start=as_datetime(rec['enrollment_start']).replace(tzinfo=utc),
                enrollment_end=as_datetime(rec['enrollment_end']).replace(tzinfo=utc),
            )
        if RELEASE_LINE != 'ginkgo':
            defaults['version'] = CourseOverview.VERSION
        CourseOverview.objects.update_or_create(
            id=as_course_key(course_id),
            defaults=defaults,
        )


def clear_non_admin_users():
    users = get_user_model().objects.exclude(
        is_superuser=True).exclude(is_staff=True)
    users.delete()


def seed_users(data=None):
    if not data:
        data = cans.USER_DATA

    first_date = days_from(LAST_DAY, DAYS_BACK * -1)
    created_users = []
    for rec in data:
        try:
            profile_rec = rec.get('profile', None)
            user = get_user_model().objects.create_user(
                username=rec['username'],
                password=rec['password'],
                email=rec['email'],
                )
            user.is_staff = rec.get('is_staff', False)
            user.is_superuser = rec.get('is_superuser', False)
            user.date_joined = as_datetime(
                FAKE.date_between(first_date, LAST_DAY)).replace(tzinfo=utc)
            user.save()
            created_users.append(user)
            if profile_rec:
                UserProfile.objects.create(
                    user=user,
                    name=profile_rec['fullname'],
                    gender=profile_rec.get('gender', None),
                    country=profile_rec.get('country', None),
                )
        except IntegrityError as e:
            print(('skipping duplicate user email {}'.format(e)))
    return created_users


def seed_course_enrollments_for_course(course_id, users, max_days_back):

    def enroll_date(max_days_back):
        days_back = random.randint(1, abs(max_days_back))
        return days_from(LAST_DAY, days_back * -1)

    for user in users:
        if VERBOSE:
            print('seeding course enrollment for user {}'.format(user.username))

        CourseEnrollment.objects.update_or_create(
            course_id=course_id,
            user=user,
            created=as_datetime(enroll_date(max_days_back)).replace(tzinfo=utc),
            )


def seed_course_enrollments():
    """
    TODO: make the number of users variable
    """
    for co in CourseOverview.objects.all():
        users = seed_users(cans.users.UserGenerator(NUM_LEARNERS_PER_COURSE))
        seed_course_enrollments_for_course(co.id, users, DAYS_BACK)


def seed_course_enrollments_multiple(user_count=10):
    """Creates a set of users and then creates course enrollments

    This function creates a set of users and creates enrollments for each user
    for every course in the site. The driver to make this is to test user
    filtering because the learner-metrics endpoint (using the UserFilterSet)
    was returning duplicates. It turns out that you need to specify 'distinct'
    in the filter class constructor.

    See here: https://github.com/appsembler/figures/pull/273
    """
    users = seed_users(cans.users.UserGenerator(user_count))
    for co in CourseOverview.objects.all():
        seed_course_enrollments_for_course(co.id, users, DAYS_BACK)
    return users


def add_users_to_site(site, users):
    """Helper function adds users to a site if not already added

    This function creates UserOrganizationMapping records for the given set of
    users.
    """
    orgs = get_organizations_for_site(site)
    if not orgs:
        print('Site "{}"" does not have any orgs'.format(site.domain))
    else:
        for org in orgs:
            for user in users:
                # assign as non-admin users
                # UserOrganizationMapping.objects.create(user=user,
                #                                        organization=org,
                #                                        is_active=True)
                UserOrganizationMapping.objects.get_or_create(
                    user=user,
                    organization=org,
                    is_active=True)


def seed_course_access_roles(data=None):
    if not data:
        data = cans.COURSE_ACCESS_ROLE_DATA

    for rec in data:
        print('creating course access role')
        CourseAccessRole.objects.update_or_create(
            user=get_user_model().objects.get(username=rec['username']),
            org=rec['org'],
            course_id=as_course_key(rec['course_id']),
            role=rec['role'],
        )


def seed_student_modules():
    """
    We're assuming active students here. Improvement is to skip a few and make
    others more active. Do it in a normal distrubution

    """
    for ce in CourseEnrollment.objects.all():
        # Added assert to check if it traps for this error:
        # ValueError: empty range for randrange() (1554681600,1554595201, -86399)
        assert ce.created <= LAST_DAY, "ce.created={}, LAST_DAY={}".format(
            ce.created, LAST_DAY)

        for i in range(random.randint(1, 5)):
            StudentModule.objects.update_or_create(
                student=ce.user,
                course_id=ce.course_id,
                created=ce.created,
                modified=as_datetime(FAKE.date_between(ce.created, LAST_DAY)),
            )


def seed_course_completions():
    """
    go over the dates
    """
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
                created_date=as_datetime(FAKE.date_between(
                    ce.created, LAST_DAY)).replace(tzinfo=utc),
            )


def seed_course_daily_metrics_fixed(data=None):
    if not data:
        data = cans.COURSE_DAILY_METRICS_DATA
    for index, rec in enumerate(data):
        print(('seed CDM # {}'.format(index)))
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
    end_date = LAST_DAY
    start_date = days_from(end_date, -DAYS_BACK)

    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        if VERBOSE:
            print(('populating day {} for course {}'.format(dt, course_id)))
        cdm, created = pipeline_cdm.CourseDailyMetricsLoader(course_id).load(
            date_for=dt, force_update=True)


def seed_course_daily_metrics():
    for co in CourseOverview.objects.all():
        if VERBOSE:
            print(('seeding CDM for course {}'.format(co.id)))
        seed_course_daily_metrics_for_course(co.id)


def seed_site_daily_metrics(data=None):
    """
    Run seed_course_daily_metrics first

    Then, for each date for which we have a CDM record
    """
    end_date = LAST_DAY
    start_date = days_from(end_date, -DAYS_BACK)
    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        pipeline_sdm.SiteDailyMetricsLoader().load(
            site=get_site(),
            date_for=dt, force_update=True)


def seed_lcgm_for_course(**_kwargs):
    """Quick hack to create a number of LCGM records
    Improvement is to add a devsite model for "synthetic course policy". This
    model specifies course info: points possible, sections possible, number of
    learners or learer range, learner completion/progress curve
    """
    date_for = _kwargs.get('date_for', datetime.datetime.utcnow().date())
    site = _kwargs.get('site', get_site())
    course_id = _kwargs.get('course_id')
    points_possible = _kwargs.get('points_possible', 20)
    points_earned = _kwargs.get('points_earned', 10)
    sections_possible = _kwargs.get('sections_possible', 10)
    sections_worked = _kwargs.get('sections_worked', 5)
    for ce in CourseEnrollment.objects.filter(course_id=as_course_key(course_id)):
        LearnerCourseGradeMetrics.objects.update_or_create(
            site=site,
            user=ce.user,
            course_id=str(course_id),
            date_for=date_for,
            defaults=dict(
                points_possible=points_possible,
                points_earned=points_earned,
                sections_possible=sections_possible,
                sections_worked=sections_worked
            )
        )


def seed_lcgm_all():
    for co in CourseOverview.objects.all():
        print(('Seeding LCGM for course {}'.format(str(co.id))))
        for i, date_for in enumerate(days_back_list(10)):
            seed_args = dict(
                date_for=date_for,
                course_id=str(co.id),
                points_possible=100,
                points_earned=i*5,
                sections_possible=20,
                sections_worked=i*2,
            )
            seed_lcgm_for_course(**seed_args)


def hotwire_multisite():
    """
    This is a quick and dirty implementation of a single site in multisite mode
    """
    params = dict(
        name='Foo Organization',
        short_name='FOO',
        description='Foo org description',
        logo=None,
        active=True,
    )
    org = Organization.objects.create(**params)
    if is_multisite():
        org.sites = [get_site()]
        org.save()

    for course in CourseOverview.objects.all():
        OrganizationCourse.objects.create(course_id=str(course.id),
                                          organization=org,
                                          active=True)
    for user in get_user_model().objects.all():
        # For now, not setting is_amc_admin roles
        UserOrganizationMapping.objects.create(user=user,
                                               organization=org,
                                               is_active=True)


def backfill_figures_ed():
    results = dict()
    for site in get_sites():
        print('Backfilling enrollment data for site "{}"'.format(site.domain))
        site_ed = backfill_enrollment_data_for_site(site)
        results[site.id] = site_ed
    return results


def wipe():
    print('Wiping synthetic data...')
    clear_non_admin_users()

    # edx-platform models
    CourseEnrollment.objects.all().delete()
    StudentModule.objects.all().delete()
    CourseOverview.objects.all().delete()

    # edx-organizations models
    Organization.objects.all().delete()
    OrganizationCourse.objects.all().delete()
    if is_multisite():
        UserOrganizationMapping.objects.all().delete()

    # Figures models
    CourseDailyMetrics.objects.all().delete()
    EnrollmentData.objects.all().delete()
    LearnerCourseGradeMetrics.objects.all().delete()
    SiteDailyMetrics.objects.all().delete()
    SiteMonthlyMetrics.objects.all().delete()


def seed_all():
    print("\nseeding mock platform models")
    print("----------------------------")
    print("seeding course overviews...")
    seed_course_overviews()
    print("seeding users...")
    seed_users()

    print("seeding course enrollments...")
    seed_course_enrollments()

    if is_multisite():
        print("Hotwiring multisite...")
        hotwire_multisite()

    print("- skipping seeding seed_course_access_roles, broken")
    # print("seeding course enrollments...")
    # seed_course_access_roles()

    print("seeding student modules...")
    seed_student_modules()
    print("seeding course completions...")
    seed_course_completions()
    print("\nseeding figures metrics models")
    print("------------------------------")
    print(("backfilling course daily metrics for {} days back...".format(DAYS_BACK)))
    print("  (this may take serveral minutes)")
    seed_course_daily_metrics()
    print("seeding site daily metrics...")
    seed_site_daily_metrics()
    print('Backfilling Figures EnrollmentData models...')
    backfill_figures_ed()
