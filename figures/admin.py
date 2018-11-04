"""Provides access to Figures models in the admin dashboard
"""

from django.contrib import admin

import figures.models


@admin.register(figures.models.CourseDailyMetrics)
class CourseDailyMetricsAdmin(admin.ModelAdmin):
    """Defines the admin interface for the CourseDailyMetrics model
    """
    list_display = ('id', 'date_for', 'course_id', 'enrollment_count',
                    'average_progress', 'average_days_to_complete',
                    'num_learners_completed',)


@admin.register(figures.models.SiteDailyMetrics)
class SiteDailyMetricsAdmin(admin.ModelAdmin):
    """Defines the admin interface for the SiteDailyMetrics model
    """
    list_display = ('id', 'date_for', 'cumulative_active_user_count',
                    'todays_active_user_count', 'total_user_count',
                    'course_count', 'total_enrollment_count',)


@admin.register(figures.models.LearnerCourseGradeMetrics)
class LearnerCourseGradeMetricsAdmin(admin.ModelAdmin):
    """Defines the admin interface for the LearnerCourseGradeMetrics model
    """
    list_display = ('id', 'date_for', 'user', 'course_id',
                    'progress_percent', 'points_possible', 'points_earned',
                    'sections_worked', 'sections_possible')


@admin.register(figures.models.PipelineError)
class PipelineErrorAdmin(admin.ModelAdmin):
    """Defines the admin interface for the PipelineError model
    """
    list_display = ('id', 'created', 'error_type', 'error_data', 'course_id',
                    'user')
