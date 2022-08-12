"""Test next iteration to collect enrollment metrics

These tests exercies the module, `figures.pipeline.enrollment_metrics_next`.

See the module docstring for details.
"""
from decimal import Decimal
import pytest
from mock import patch

from django.contrib.sites.models import Site
from django.forms import DecimalField

from figures.compat import CourseEnrollment
from figures.pipeline.enrollment_metrics_next import (
    update_enrollment_data_for_course,
    stale_course_enrollments,
    calculate_course_progress,
)
from figures.sites import UnlinkedCourseError

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    EnrollmentDataFactory,
    StudentModuleFactory,
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
class TestStaleCourseEnrollments(object):
    """Tests `stale_course_enrollments`
    """

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        self.course_overview = CourseOverviewFactory()
        self.site = Site.objects.first()

    def test_empty_course_list_comprehension(self):
        found = [rec for rec in stale_course_enrollments(self.course_overview.id)]
        assert found == []

    def test_emtpy_course_next(self):
        # import pdb; pdb.set_trace()

        with pytest.raises(StopIteration):
            rec = next(stale_course_enrollments(self.course_overview.id))


    def test_no_update_needed(self, monkeypatch):
        """Call to function yields no results

        This test and the next one, 'test_needs_update' do "all or nothing" for
        returning boolean values from `is_enrollment_out_of_date`. That's ok,
        because there's test coverage specifically for this function in `test_enrollments.py`
        So as long as this function has unit tests for its possible states, we
        don't need to do it here.
        """
        # Need to mock/monkeypatch. Either code within 'is_enrollment_data_out_of_date'
        # or the function itself.
        # See test_enrollment.py::TestIsEnrollmentDataOutOfDate

        ce_recs = [CourseEnrollmentFactory(course_id=self.course_overview.id) for _ in range(2)]
        [StudentModuleFactory.from_course_enrollment(ce) for ce in ce_recs]
        monkeypatch.setattr('figures.pipeline.enrollment_metrics_next.is_enrollment_data_out_of_date', lambda val: False)
        assert not [rec for rec in stale_course_enrollments(self.course_overview.id)]

    def test_needs_update(self, monkeypatch):
        """Call to function yields two results

        We create three enrollments and leave one enrollment without any StudentModule
        """
        ce = [CourseEnrollmentFactory(course_id=self.course_overview.id) for _ in range(3)]
        StudentModuleFactory.from_course_enrollment(ce[0])
        StudentModuleFactory.from_course_enrollment(ce[1])
        monkeypatch.setattr('figures.pipeline.enrollment_metrics_next.is_enrollment_data_out_of_date', lambda val: True)
        found = [rec for rec in stale_course_enrollments(self.course_overview.id)]
        assert set(found) == set(ce[:2])


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

        The average progress calculator should round the number with a precision
        of 3 and a scale of two (two digits to the right of the decimal point)
        """
        some_percentages = [0.0, 0.25, 0.50, 0.66]
        expected_average = sum(some_percentages)/len(some_percentages)
        expected_average = float(Decimal(expected_average).quantize(Decimal('.00')))
        [
            EnrollmentDataFactory(course_id=str(self.course_overview.id), progress_percent=pp)
            for pp in some_percentages
        ]
        results = calculate_course_progress(self.course_overview.id)
        assert results['average_progress'] == pytest.approx(expected_average)

        # Crude, but checks that we meet the fixed decimal precision requirements
        # This will raise a django.core.exceptions.ValidationError if it doesn't pass
        DecimalField(max_digits=3, decimal_places=2).clean(results['average_progress'])


    def test_calc_course_progress_invalid_values(self):
        """ Placeholder test method

        Not implementing this yet, but included this test method to consider if
        we should add a test for when invalid values are stored in the
        EnrollmentData.progress_percent field
        """
        pass
