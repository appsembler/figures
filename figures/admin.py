'''Provides access to Figures models in the admin dashboard

'''

from django.contrib import admin

# Register your models here.

from .models import (
    CourseDailyMetrics,
    SiteDailyMetrics,
    )


@admin.register(CourseDailyMetrics)
class CourseDailyMetricsAdmin(admin.ModelAdmin):
    '''Defines the admin interface for the CourseDailyMetrics model
    '''
    list_display = ('id', 'date_for', 'course_id', 'enrollment_count',
                    'average_progress', 'average_days_to_complete',
                    'num_learners_completed',)


@admin.register(SiteDailyMetrics)
class SiteDailyMetricsAdmin(admin.ModelAdmin):
    '''Defines the admin interface for the SiteDailyMetrics model
    '''
    list_display = ('id', 'date_for', 'cumulative_active_user_count',
                    'todays_active_user_count', 'total_user_count',
                    'course_count', 'total_enrollment_count',)
