"""Unit tests for figures.admin

"""

import pytest

from django.contrib.admin.sites import AdminSite

from figures.admin import (
    CourseDailyMetricsAdmin,
    SiteDailyMetricsAdmin,
    LearnerCourseGradeMetricsAdmin,
    PipelineErrorAdmin,
    )
from figures.models import (
    CourseDailyMetrics,
    SiteDailyMetrics,
    LearnerCourseGradeMetrics,
    PipelineError,
    )

@pytest.mark.django_db
class TestModelAdminRepresentations(object):
    """Initial tests doing basic coverage

    """

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.admin_site = AdminSite()

    @pytest.mark.parametrize('model_class, model_admin_class', [
            (CourseDailyMetrics, CourseDailyMetricsAdmin),
            (SiteDailyMetrics, SiteDailyMetricsAdmin),
            (LearnerCourseGradeMetrics, LearnerCourseGradeMetricsAdmin),
            (PipelineError, PipelineErrorAdmin),
        ])
    def test_course_daily_metrics_admin(self, model_class, model_admin_class):
        obj = model_admin_class(model_class, self.admin_site)
        assert obj.list_display
