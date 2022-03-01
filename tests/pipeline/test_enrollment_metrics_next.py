"""Test next iteration to collect enrollment metrics

These tests exercies the module, `figures.pipeline.enrollment_metrics_next`.

See the module docstring for details.
"""
import pytest
from mock import patch

from django.contrib.sites.models import Site

from figures.compat import CourseEnrollment
from figures.pipeline.enrollment_metrics_next import (
    update_enrollment_data_for_course,
    calculate_course_progress,
)
from figures.sites import UnlinkedCourseError

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    EnrollmentDataFactory,
)


@pytest.mark.django_db
class TestUpdateMetrics(object):
    """Tests `update_enrollment_data_for_course`

    Since `figures.models.EnrollmentDataManager.update_metrics` is tested in
    `tests/models/test_enrollment_data_update_metrics.py`, we can mock this
    method in our tests here.
    """

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        self.course_overview = CourseOverviewFactory()
        self.site = Site.objects.first()

    def test_course_has_no_enrollments(self, monkeypatch):
        """We have a new course with no enrollments
        """
        monkeypatch.setattr('figures.course.get_site_for_course', lambda val: self.site)
        result = update_enrollment_data_for_course(self.course_overview.id)
        assert result == []

    def test_course_has_enrollments_but_no_active_for_yesterday(self, monkeypatch):
        """We have enrollments, but none were active yesterday
        """
        monkeypatch.setattr('figures.course.get_site_for_course', lambda val: self.site)
        [CourseEnrollmentFactory(course_id=self.course_overview.id)
         for _ in range(2)]
        result = update_enrollment_data_for_course(self.course_overview.id)
        assert result == []

    def test_course_has_active_enrollments_for_yesterday(self):
        """We have enrollments who were active yesterday
        """
        expected_ce = [CourseEnrollmentFactory(course_id=self.course_overview.id)
                       for _ in range(2)]
        ce = CourseEnrollment.objects.filter(course_id=self.course_overview.id)

        def mock_update_metrics(site, ce):
            return ce

        with patch('figures.pipeline.enrollment_metrics_next.Course') as course_class:
            with patch('figures.pipeline.enrollment_metrics_next.EnrollmentData.objects') as edm:
                course_class.return_value.enrollments_active_on_date.return_value = ce
                course_class.return_value.site = self.site
                edm.update_metrics = mock_update_metrics
                result = update_enrollment_data_for_course(self.course_overview.id)
                assert set(result) == set(expected_ce)

    def test_course_is_unlinked(self, monkeypatch):
        """Function should raise `UnlinkedCourseError` if there's not a site match

        For Tahoe's multisite implementation, this can happen if the course's
        organization is not linked to a site
        For standalone sites, this should never happen

        To learn more, see the `figures.sites.get_site_for_course` function.
        """
        monkeypatch.setattr('figures.course.get_site_for_course', lambda val: None)
        with pytest.raises(UnlinkedCourseError) as excinfo:
            update_enrollment_data_for_course(self.course_overview.id)
        # with patch('figures.pipeline.enrollment_metrics_next.Course') as course_class:
        #     course_class.return_value.site = None
        #     with pytest.raises(UnlinkedCourseError) as excinfo:
        #         update_enrollment_data_for_course(self.course_overview.id)
        expected_msg = 'No site found for course "{}"'.format(str(self.course_overview.id))
        assert str(excinfo.value) == expected_msg


@pytest.mark.django_db
class TestCalculateProgress(object):
    """Tests `calculate_course_progress`
    """
    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        self.course_overview = CourseOverviewFactory()

    def test_calc_course_progress_empty(self):
        """The course doesn't have any EnrollmentData records
        """
        results = calculate_course_progress(self.course_overview.id)
        assert results['average_progress'] == pytest.approx(0.0)

    def test_calc_course_progress(self):
        """The course has EnrollmentData records
        """
        some_percentages = [0.0, 25.0, 50.0]
        expected_average = sum(some_percentages)/len(some_percentages)
        [
            EnrollmentDataFactory(course_id=str(self.course_overview.id), progress_percent=pp)
            for pp in some_percentages
        ]
        results = calculate_course_progress(self.course_overview.id)
        assert results['average_progress'] == pytest.approx(expected_average)
