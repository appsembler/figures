"""Test Figures backfill Celery tasks
"""
from __future__ import absolute_import

from figures.tasks import backfill_enrollment_data_for_course

from tests.factories import EnrollmentDataFactory


def test_backfill_enrollment_data_for_course(transactional_db, monkeypatch):
    """
    The Celery task is a simple wrapper around the pipeline function
    """
    course_id = 'course-v1:SomeOrg+SomeNum+SomeRun'
    ed_recs = [EnrollmentDataFactory() for _ in range(2)]

    func_path = 'figures.tasks.update_enrollment_data_for_course'
    monkeypatch.setattr(func_path, lambda course_id: ed_recs)
    ed_ids = backfill_enrollment_data_for_course(course_id)
    assert set(ed_ids) == set([obj.id for obj in ed_recs])
