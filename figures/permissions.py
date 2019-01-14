'''Provides permissions for Figures views

'''
from rest_framework.permissions import BasePermission

import django.contrib.sites.shortcuts

import organizations

import figures.settings


def is_site_admin_user(request):

    if not figures.settings.is_multisite():
        has_permission = IsStaffUser().has_permission(request, None)
    else:
        current_site = django.contrib.sites.shortcuts.get_current_site(request)
        # get orgs for the site
        orgs = organizations.models.Organization.objects.filter(sites__in=[current_site])
        # Should just be mappings for organizations in this site
        # If just one organization in a site, then the queryset returned
        # should contain just one element
        uom_qs = organizations.models.UserOrganizationMapping.objects.filter(
            organization__in=orgs,
            user=request.user)
        # Since Tahoe does just one org, we're going to cheat and just look
        # for the first element
        if uom_qs:
            has_permission = uom_qs[0].is_amc_admin and uom_qs[0].is_active
        else:
            has_permission = False
    return has_permission


def is_active_staff_or_superuser(request):
    return request.user and request.user.is_active and (
           request.user.is_staff or request.user.is_superuser)


class IsStaffUser(BasePermission):
    """
    Allow access to only active staff users or superusers
    """
    def has_permission(self, request, view):
        return is_active_staff_or_superuser(request)


class IsSiteAdminUser(BasePermission):
    """
    Allow access to only site admins if in multisite mode or staff or superuser
    if in standalone mode
    """
    def has_permission(self, request, view):
        return is_site_admin_user(request)
