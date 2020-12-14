"""Provides access to Figures models in the admin dashboard

Filters are in this module because they are specific to the admin console
"""

from __future__ import absolute_import
from django.contrib import admin
from django.contrib.admin.filters import (
    AllValuesFieldListFilter,
    RelatedOnlyFieldListFilter)
from django.utils.html import format_html

try:
    # Django 2.0+
    from django.urls import reverse
except ImportError:
    # Django <1.9
    from django.core.urlresolvers import reverse

import figures.models


class AllValuesDropdownFilter(AllValuesFieldListFilter):
    """Show dropdown when there are more than three filter choices for this field
    """
    template = 'figures/admin_dropdown_filter.html'


class RelatedOnlyDropdownFilter(RelatedOnlyFieldListFilter):
    """Show dropdown when there are more than three filter choices for this field
    """
    template = 'figures/admin_dropdown_filter.html'


@admin.register(figures.models.CourseDailyMetrics)
class CourseDailyMetricsAdmin(admin.ModelAdmin):
    """Defines the admin interface for the CourseDailyMetrics model
    """
    list_display = ('id', 'date_for', 'site', 'course_id', 'enrollment_count',
                    'average_progress', 'average_days_to_complete',
                    'num_learners_completed')
    list_filter = (
        ('site', RelatedOnlyDropdownFilter),
        ('course_id', AllValuesDropdownFilter),
        'date_for')


@admin.register(figures.models.SiteDailyMetrics)
class SiteDailyMetricsAdmin(admin.ModelAdmin):
    """Defines the admin interface for the SiteDailyMetrics model
    """
    list_display = ('id', 'date_for', 'site', 'cumulative_active_user_count',
                    'todays_active_user_count', 'total_user_count',
                    'course_count', 'total_enrollment_count',)
    list_filter = (
        ('site', RelatedOnlyDropdownFilter),
        'date_for')


@admin.register(figures.models.SiteMonthlyMetrics)
class SiteMonthlyMetricsAdmin(admin.ModelAdmin):
    """Defines the admin interface for the SiteMonthlyMetrics model
    """
    list_display = ('id', 'month_for', 'site', 'active_user_count')
    list_filter = (
        ('site', RelatedOnlyDropdownFilter),
        'month_for')


class UserRelatedMixin(object):
    """Provides search box on user properties and a user link method

    To use:
    1. Include this class in the base classes
    2. add 'user_link' to 'list_display'

    """
    search_fields = ('user__username', 'user__email', 'user__profile__name')

    def user_link(self, obj):
        if obj.user:
            return format_html(
                '<a href="{}">{}</a>',
                reverse("admin:auth_user_change", args=(obj.user.pk,)),
                obj.user.email)
        else:
            return 'Missing user'


@admin.register(figures.models.EnrollmentData)
class EnrollmentDataAdmin(UserRelatedMixin, admin.ModelAdmin):
    """Defines the admin interface for the EnrollmentData model
    """
    list_display = (
        'id', 'site', 'user_link', 'course_id', 'date_enrolled', 'date_for',
        'is_enrolled', 'is_completed', 'progress_percent', 'points_earned',
        'points_possible', 'sections_worked', 'sections_possible'
    )
    read_only_fields = ('site', 'user', 'user_link', 'course_id')
    list_filter = (
        ('site', RelatedOnlyDropdownFilter),
        ('course_id', AllValuesDropdownFilter),
        'date_for',
        'date_enrolled',
        'is_enrolled',
        'is_completed')


@admin.register(figures.models.LearnerCourseGradeMetrics)
class LearnerCourseGradeMetricsAdmin(UserRelatedMixin, admin.ModelAdmin):
    """Defines the admin interface for the LearnerCourseGradeMetrics model
    """
    list_display = ('id', 'date_for', 'site', 'user_link', 'course_id',
                    'progress_percent', 'points_possible', 'points_earned',
                    'sections_worked', 'sections_possible')
    list_filter = (
        ('site', RelatedOnlyDropdownFilter),
        ('course_id', AllValuesDropdownFilter),
        'date_for')
    read_only_fields = ('user', 'user_link')


@admin.register(figures.models.PipelineError)
class PipelineErrorAdmin(admin.ModelAdmin):
    """Defines the admin interface for the PipelineError model
    """
    list_display = ('id', 'site', 'course_id', 'created', 'error_type',
                    'error_data', 'course_id', 'user')
    list_filter = (
        ('site', RelatedOnlyDropdownFilter),
        ('course_id', AllValuesDropdownFilter),
        ('user', RelatedOnlyFieldListFilter),
        'error_type')


@admin.register(figures.models.CourseMauMetrics)
class CourseMauMetricsAdmin(admin.ModelAdmin):
    """Defines the admin interface for the CourseMauMetrics model
    """
    list_display = ('id', 'date_for', 'site', 'course_id', 'mau')
    list_filter = (
        ('site', RelatedOnlyDropdownFilter),
        ('course_id', AllValuesDropdownFilter),
        'date_for')
