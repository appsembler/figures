"""

figuers.sites provides a single point to retrieve site specific data

In general, the rest of Figures should call this module to retrieve all site
specific data in edx-platform, such as users, course overviews, and
course enrollments as examples

TODO:
Document how organization site mapping works
"""

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.conf import settings

# TODO: Add exception handling
import organizations

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)
from student.models import CourseEnrollment

from figures.helpers import as_course_key
import figures.helpers


def default_site():
    """Returns the default site instance if Django settings defines SITE_ID, else None

    Tech debt note: Open edX monkeypatches django.contrib.sites to override
    behavior for getting the current site.
    """
    if getattr(settings, 'SITE_ID', ''):
        return Site.objects.get(pk=settings.SITE_ID)


def get_site_for_course(course_id):
    """
    Given a course, return the related site or None

    For standalone mode, will always return the site
    For multisite mode, will return the site if there is a mapping between the
    course and the site. Otherwise `None` is returned

    # Implementation notes

    There should be only one organization per course.
    TODO: Figure out how we want to handle ``DoesNotExist``
    whether to let it raise back up raw or handle with a custom exception
    """
    if figures.helpers.is_multisite():
        org_courses = organizations.models.OrganizationCourse.objects.filter(
            course_id=str(course_id))
        if org_courses:
            # Keep until this assumption analyzed
            msg = 'Multiple orgs found for course: {}'
            assert org_courses.count() == 1, msg.format(course_id)
            first_org = org_courses.first().organization
            if hasattr(first_org, 'sites'):
                msg = 'Must have one and only one site. Org is "{}"'
                assert first_org.sites.count() == 1, msg.format(first_org.name)
                site = first_org.sites.first()
            else:
                site = None
        else:
            # We don't want to make assumptions of who our consumers are
            # TODO: handle no organizations found for the course
            site = None
    else:
        # Operating in single site / standalone mode, return the default site
        site = Site.objects.get(id=settings.SITE_ID)
    return site


def get_organizations_for_site(site):
    """
    TODO: Refactor the functions in this module that make this call
    """
    return organizations.models.Organization.objects.filter(sites__in=[site])


def get_course_keys_for_site(site):
    if figures.helpers.is_multisite():
        orgs = organizations.models.Organization.objects.filter(sites__in=[site])
        org_courses = organizations.models.OrganizationCourse.objects.filter(
            organization__in=orgs)
        course_ids = org_courses.values_list('course_id', flat=True)
    else:
        course_ids = CourseOverview.objects.all().values_list('id', flat=True)
    return [as_course_key(cid) for cid in course_ids]


def get_courses_for_site(site):
    """Returns the courses accessible by the user on the site

    This function relies on Appsembler's fork of edx-organizations
    """
    if figures.helpers.is_multisite():
        course_keys = get_course_keys_for_site(site)
        courses = CourseOverview.objects.filter(id__in=course_keys)
    else:
        courses = CourseOverview.objects.all()
    return courses


def get_user_ids_for_site(site):
    if figures.helpers.is_multisite():
        orgs = organizations.models.Organization.objects.filter(sites__in=[site])
        mappings = organizations.models.UserOrganizationMapping.objects.filter(
            organization__in=orgs)
        user_ids = mappings.values_list('user', flat=True)
    else:
        user_ids = get_user_model().objects.all().values_list('id', flat=True)
    return user_ids


def get_users_for_site(site):
    if figures.helpers.is_multisite():
        user_ids = get_user_ids_for_site(site)
        users = get_user_model().objects.filter(id__in=user_ids)
    else:
        users = get_user_model().objects.all()
    return users


def get_course_enrollments_for_site(site):
    course_keys = get_course_keys_for_site(site)
    return CourseEnrollment.objects.filter(course_id__in=course_keys)
