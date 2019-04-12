'''Provides permissions for Figures views

'''
from rest_framework.permissions import BasePermission

import django.contrib.sites.shortcuts

import organizations

import figures.helpers
import figures.sites


class MultipleOrgsPerUserNotSupported(Exception):
    pass


def is_active_staff_or_superuser(request):
    """
    Standalone mode authorization check
    """
    return request.user and request.user.is_active and (
           request.user.is_staff or request.user.is_superuser)


def is_site_admin_user(request):
    """
    Determines if the requesting user has access to site admin data

    * If Figures is running in standalone mode, then the user needs to be staff
      or superuser.
    * If figures is running in multisite mode, then the user needs to belong to
      the site through the site's organization and have admin permission for
      that organization or have staff or superuser access.

    ## Multisite implementation

    This initial multisite implementation assumes a user belongs to only one
    organization in a site. This is represented in the UserOrganizationMapping
    model in Appsembler's fork of edx-organizations. This model currently does
    not enforce user-org uniquness. Therefore, multiple records returned is an
    error and the behavior is undefined. Multiple user organiazation mappings
    found will raise an exception to prevent returning invalid authorization.

    To support multiple user organization mappings per site, we need to
    determine the authorization criteria in that environment.

    Note: Depending on community participation, we may make this a pluggable
    feature but there are other considerations such as future built-in support
    for site and organization access control in the futire.


    ## What this function does

    1. Get the current site (matching the request)
    2. Get the orgs for the site. We assume only one org
    3. Get the user org mappings for the orgs and user in the request
    4. Check the uom record if user is admin and active
    """
    has_permission = is_active_staff_or_superuser(request)
    if not has_permission:
        if figures.helpers.is_multisite():
            current_site = django.contrib.sites.shortcuts.get_current_site(request)
            orgs = organizations.models.Organization.objects.filter(sites__in=[current_site])
            # Should just be mappings for organizations in this site
            # If just one organization in a site, then the queryset returned
            # should contain just one element
            uom_qs = organizations.models.UserOrganizationMapping.objects.filter(
                organization__in=orgs,
                user=request.user)

            # This is here to Fail because multiple orgs per site is unsupported
            if uom_qs.count() > 1:
                raise MultipleOrgsPerUserNotSupported(
                    'Only one org per user per site is allowed. found {}'.format(
                        uom_qs.count())
                    )
            # Since Tahoe does just one org, we're going to cheat and just look
            # for the first element
            if uom_qs and request.user.is_active:
                has_permission = uom_qs[0].is_amc_admin and uom_qs[0].is_active
            else:
                has_permission = False
        else:
            has_permission = is_active_staff_or_superuser(request)
    return has_permission


def is_staff_user_on_default_site(request):
    """Allow access to only global staff or superusers accessing the default site
    """
    default_site = figures.sites.default_site()
    if default_site and is_active_staff_or_superuser(request):
        current_site = django.contrib.sites.shortcuts.get_current_site(request)
        return current_site == default_site
    return False


class IsSiteAdminUser(BasePermission):
    """
    Allow access to only site admins if in multisite mode or staff or superuser
    if in standalone mode

    Would `has_object_permission` help simplify filtering by site?
    """
    def has_permission(self, request, view):
        return is_site_admin_user(request)


class IsStaffUserOnDefaultSite(BasePermission):
    """Allow access to only global staff or superusers accessing the default site
    """
    def has_permission(self, request, view):
        return is_staff_user_on_default_site(request)
