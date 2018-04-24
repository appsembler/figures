from django.contrib import admin

# Register your models here.

from .models import (
    SiteDailyMetrics,

    )

@admin.register(SiteDailyMetrics)
class SiteDailyMetricsAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'date_for', 'cumulative_active_user_count',
        'todays_active_user_count', 'total_user_count',
        'course_count', 'total_enrollment_count',
        )
