"""Figures query interface

This module was created to simplify testing and debugging queries used in
Figures API views. That is not its only goal, just where we're starting

"""
from django.contrib.auth import get_user_model
from django.db.models import Q


def site_users_enrollment_data(site, course_ids=None, user_term=None):
    """Retrieve queryset for users with enrollments

    This queryset runs 'select_related' to include the UserProfile records
    and runs 'prefetch_related' to include the EnrollmentData records.

    This queryset will return all site users and enrollments unless one or both
    of the 'course_ids' and 'user_filter' parameters are set.

    If 'course_ids' is None or an empty list then the queryset will return only
    users who are enrolled in those courses
    If 'user_filer' is not null then a search is made on the username, email
    and profile name fields to match the search term as a substring

    If both 'course_ids' and 'user_filter' are used then a queryset matching
    the intersection will be returned
    """
    qs = get_user_model().objects.filter(
        enrollmentdata__site_id=site.id).select_related(
        'profile').prefetch_related('enrollmentdata_set')

    if course_ids:
        qs = qs.filter(enrollmentdata__course_id__in=course_ids)

    if user_term:
        qs = qs.filter(Q(username__contains=user_term) |
                       Q(email__contains=user_term) |
                       Q(profile__name__contains=user_term))

    return qs.distinct()
