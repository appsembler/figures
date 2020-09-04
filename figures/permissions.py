"""Provides permissions for Figures views

"""
from __future__ import absolute_import
from rest_framework.permissions import BasePermission

import django.contrib.sites.shortcuts

from organizations.models import Organization

try:
    from organizations.models import UserOrganizationMapping
except ImportError:
    pass

import figures.helpers
import figures.sites


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
      an organizations mapped to the specified site and have `is_amc_admin` set
      to `True`

    ## What this function does

    1. Get the current site (matching the request)
    2. Get the orgs for the site. We assume only one org
    3. Get the user org mappings for the orgs and user in the request
    4. Check the uom record if user is admin and active
    """
    has_permission = is_active_staff_or_superuser(request)
    if not has_permission:
        if figures.helpers.is_multisite():
            if request.user.is_active:
                current_site = django.contrib.sites.shortcuts.get_current_site(request)
                org_ids = Organization.objects.filter(
                    sites__in=[current_site]).values_list('id',
                                                          flat=True)
                return UserOrganizationMapping.objects.filter(
                    organization_id__in=org_ids,
                    user=request.user,
                    is_active=True,
                    is_amc_admin=True).exists()
            else:
                return False
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
