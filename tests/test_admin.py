"""Unit tests for figures.admin

"""

from __future__ import absolute_import
import pytest

from django.contrib.admin.sites import AdminSite

import figures.admin

from figures.models import (
    CourseDailyMetrics,
    SiteDailyMetrics,
    SiteMonthlyMetrics,
    LearnerCourseGradeMetrics,
    PipelineError,
    CourseMauMetrics,
    )

from tests.factories import (
    LearnerCourseGradeMetricsFactory,
    UserFactory,
    )


@pytest.mark.django_db
class TestModelAdminRepresentations(object):
    """Initial tests doing basic coverage

    """

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.admin_site = AdminSite()

    @pytest.mark.parametrize('model_class, model_admin_class', [
            (CourseDailyMetrics, figures.admin.CourseDailyMetricsAdmin),
            (SiteDailyMetrics, figures.admin.SiteDailyMetricsAdmin),
            (SiteMonthlyMetrics, figures.admin.SiteMonthlyMetricsAdmin),
            (LearnerCourseGradeMetrics, figures.admin.LearnerCourseGradeMetricsAdmin),
            (PipelineError, figures.admin.PipelineErrorAdmin),
            (CourseMauMetrics, figures.admin.CourseMauMetricsAdmin),
        ])
    def test_metrics_model_admin(self, model_class, model_admin_class):
        obj = model_admin_class(model_class, self.admin_site)
        assert obj.list_display


@pytest.mark.django_db
class TestLearnerCourseGradeMetricsAdmin(object):
    """
    LearnerCourseGradesMetricsAdmin class has a member method to provide a link
    to the user page in admin
    """

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.admin_site = AdminSite()

    def test_user_link(self, monkeypatch):
        """Tests the two cases of user link
        A) there is a user in the record
        B) there is not a user in the record
        """
        mock_uri = '/mock-uri-to-user-admin-page'

        def mock_reverse(*args, **kwargs):
            return mock_uri

        users = [UserFactory(), UserFactory()]
        lcg_metrics = [
            LearnerCourseGradeMetricsFactory(user=users[0]),
            LearnerCourseGradeMetricsFactory(user=users[1])]
        admin_obj = figures.admin.LearnerCourseGradeMetricsAdmin(
            LearnerCourseGradeMetrics, self.admin_site)
        monkeypatch.setattr(figures.admin, 'reverse', mock_reverse)
        data = admin_obj.user_link(lcg_metrics[0])
        assert data == '<a href="{url}">{email}</a>'.format(url=mock_uri,
                                                            email=lcg_metrics[0].user.email)
        data = admin_obj.user_link(LearnerCourseGradeMetricsFactory(user=None))
        assert data == 'Missing user'
