'''Provides permissions for Figures views

'''
from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """
    Allow access to only staff users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_active and (
            request.user.is_staff or request.user.is_superuser)
