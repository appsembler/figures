'''Provides permissions for Figures views

'''
from rest_framework.permissions import BasePermission

import django.contrib.sites.shortcuts

import organizations.models

import figures.settings


def is_site_admin_user(request):

    if not figures.settings.is_multi_tenant():
        return IsStaffUser().has_permission(request, None)

    current_site = django.contrib.sites.shortcuts.get_current_site(request)

    try:
        obj = organizations.models.UserSiteMapping.objects.get(
            site=current_site,
            user=request.user)
        return obj.is_amc_admin
    except organizations.models.UserSiteMapping.DoesNotExist:
        return False


class IsStaffUser(BasePermission):
    """
    Allow access to only staff users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_active and (
            request.user.is_staff or request.user.is_superuser)


class IsSiteAdminUser(BasePermission):
    """

    We need to stick with a Site Admin unless we have a way to identify the org
    from the URL/host/virtual host

    If we can't use OrgSiteMapping, then we have to figure out what we're going
    to do

    Have 'OrgDailyMetrics instead of SiteDailyMetrics?'

    For prototyping

    If we are multi-site

    Why don't UserOrganizationMapping and UserSiteMapping have

    orgs_for_site = Organization.objects.filter(sites__in=[current_site,])
    UserOrganizationMapping.objects.filter()

    """
    def has_permission(self, request, view):

        # is a 'Site' model instance
        # if the site passed is not in the Site table, then the default site
        # is returned
        return is_site_admin_user(request)

        # current_site = django.contrib.sites.shortcuts.get_current_site(request)

        # try:
        #     obj = UserSiteMapping.objects.get(site=current_site,user=request.user)
        #     return obj.is_amc_admin
        # except UserSiteMapping.DoesNotExist:
        #     return False
