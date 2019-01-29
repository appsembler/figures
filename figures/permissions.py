'''Provides permissions for Figures views

'''
import logging

from rest_framework.permissions import BasePermission

import organizations

import figures.settings
import figures.sites

logger = logging.getLogger(__name__)


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
      that organization

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
    if figures.settings.is_multisite():
        current_site = figures.sites.get_current_site(request)
        orgs = organizations.models.Organization.objects.filter(sites__in=[current_site])
        # Should just be mappings for organizations in this site
        # If just one organization in a site, then the queryset returned
        # should contain just one element
        uom_qs = organizations.models.UserOrganizationMapping.objects.filter(
            organization__in=orgs,
            user=request.user)

        msg = 'figures.permissions.is_site_admin_user: current_site={}'
        msg += ', user_id={},'
        if uom_qs:
            msg += 'uom record:is_amc_admin={}, is_active={}'.format(
                uom_qs[0].is_amc_admin, uom_qs[0].is_active)
        logger.info(msg.format(current_site.domain, request.user.id))

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
            msg = 'figures.permissions.is_site_admin_user. Has permission = {}'
            logger.info(msg.format(has_permission))
        else:
            has_permission = False
    else:
        has_permission = is_active_staff_or_superuser(request)
        msg = 'figures.permissions.is_site_admin_user [Standalone mode]. '
        msg += 'user={}, has_permission={}'.format(request.user.id, has_permission)
        logger.info(msg)

    msg = 'user "" is_site_admin_user = {}'
    logger.info(msg.format(request.user.username, has_permission))
    return has_permission


class IsSiteAdminUser(BasePermission):
    """
    Allow access to only site admins if in multisite mode or staff or superuser
    if in standalone mode

    Would `has_object_permission` help simplify filtering by site?
    """
    def has_permission(self, request, view):
        return is_site_admin_user(request)
