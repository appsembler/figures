"""Test Figures backfill Celery tasks
"""
from __future__ import absolute_import
import logging
import mock
import pytest

from figures.tasks import backfill_enrollment_data_for_course

from tests.factories import EnrollmentDataFactory


@pytest.mark.django_db
class TestBackfillEnrollmentDataForCourse(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.expected_message_template = (
            'figures.tasks.backfill_enrollment_data_for_course "{course_id}".'
            ' Updated {edrec_count} enrollment data records.')

    def test_backfill_enrollment_data_for_course_no_update(self, transactional_db,
                                                           monkeypatch, caplog):
        """
        The Celery task is a simple wrapper around the pipeline function
        """
        course_id = 'course-v1:SomeOrg+SomeNum+SomeRun'

        # The function returns a list of tuples with (object, created)
        # ed_recs = [(EnrollmentDataFactory(), False) for _ in range(2)]
        caplog.set_level(logging.INFO)
        func_path = 'figures.tasks.stale_course_enrollments'
        monkeypatch.setattr(func_path, lambda course_id: [])
        backfill_enrollment_data_for_course(course_id)
        assert len(caplog.records) == 1
        assert caplog.records[0].message == self.expected_message_template.format(
            course_id=course_id,
            edrec_count=0)

    def test_backfill_enrollment_data_for_course_with_updates(self, transactional_db,
                                                              monkeypatch, caplog):
        """
        The Celery task is a simple wrapper around the pipeline function
        """
        course_id = 'course-v1:SomeOrg+SomeNum+SomeRun'

        # The function returns a list of tuples with (object, created)
        ed_recs = [(EnrollmentDataFactory(), False) for _ in range(2)]
        caplog.set_level(logging.INFO)
        monkeypatch.setattr('figures.tasks.stale_course_enrollments', lambda course_id: ed_recs)
        with mock.patch('figures.tasks.EnrollmentData') as mock_ed_class:
            mock_ed_class.return_value.objects.update_metrics.return_value = ed_recs
            backfill_enrollment_data_for_course(course_id)

        assert len(caplog.records) == 1
        assert caplog.records[0].message == self.expected_message_template.format(
            course_id=course_id,
            edrec_count=len(ed_recs))
