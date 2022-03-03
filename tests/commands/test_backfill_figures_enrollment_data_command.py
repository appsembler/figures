"""Test Figures Django management commands
"""
from __future__ import absolute_import

import pytest
import mock

from django.core.management import call_command

from tests.factories import CourseOverviewFactory, SiteFactory


@pytest.mark.django_db
class TestBackfillEnrollmentDataCommand(object):
    """Tests Django managmeent command, 'backfill_figures_enrollment_data'

    Alternate testing approach

    * Directly test the `Command.update_enrollments(...) method to make sure
      this method is correct
    * Mock `Command.update_enrollments(...)` for testing each of the following
      cases:
        * has one site domain, has two site domains
        * has one course id, has two course ids
        * has one or more site domains, and one or more courses
            * expects to ignore the sites arg and only process the courses arg
    """
    TASK = 'figures.tasks.backfill_enrollment_data_for_course'
    MANAGEMENT_COMMAND = 'backfill_figures_enrollment_data'

    @pytest.mark.parametrize('domains', [
        ['alpha.test'], ['alpha.test', 'bravo.test']
    ])
    @pytest.mark.parametrize('delay_suffix, do_delay', [
        ('', False), ('.delay', True)
    ])
    def test_backfill_with_sites_arg(self, domains, delay_suffix, do_delay):
        sites = [SiteFactory(domain=domain) for domain in domains]
        courses = [CourseOverviewFactory() for _ in range(2)]
        course_ids = [str(obj.id) for obj in courses]
        courses_for_sites = [course_ids for _ in range(len(domains))]
        calls = []
        for _ in range(len(sites)):
            calls += [mock.call(course_id) for course_id in course_ids]
        kwargs = {'sites': domains, 'use_celery': do_delay}

        with mock.patch('figures.sites.site_course_ids') as mock_site_course_ids:
            # Build thed list of the course_ids returned for each call to `site_course_ids`
            mock_site_course_ids.return_value = courses_for_sites
            with mock.patch(self.TASK + delay_suffix) as mock_task:
                call_command(self.MANAGEMENT_COMMAND, **kwargs)
                assert mock_task.has_calls(calls)

    @pytest.mark.parametrize('course_ids', [
        ['course-v1:TestOrg+T01+run'],
        ['course-v1:TestOrg+T01+run', 'course-v1:TestOrg+T02+run'],
    ])
    def test_backfill_with_courses_arg_immediate(self, course_ids):
        """Test called with courses arg and not run in Celery worker

        This tests that the expected task function is called with specific
        parameters and the `.delay(course_id)` is not called.

        This and the following function are almost identical.
        They can be merged as one test method, but for now left as two
        test methods initially for readability and the additional development
        time to implement it.

        But, should we merge them, we add an additional parametrize decorator
        like so:
        ```
        @pytest.mark.parametrize('delay_suffix, delay_flag', [
            ('', False), ('.delay', True)
        ])
        ```
        And then we abstract the nested mocks to swap the `.has_calls` and
        `not called` checks (which might require a conditional)
        """
        [CourseOverviewFactory(id=cid) for cid in course_ids]
        kwargs = {'courses': course_ids, 'use_celery': False}
        calls = [mock.call(course_id) for course_id in course_ids]

        with mock.patch(self.TASK) as mock_task:
            with mock.patch(self.TASK + '.delay') as mock_task_delay:
                call_command(self.MANAGEMENT_COMMAND, **kwargs)
                assert mock_task.has_calls(calls)
                assert not mock_task_delay.called

    @pytest.mark.parametrize('course_ids', [
        ['course-v1:TestOrg+T01+run'],
        ['course-v1:TestOrg+T01+run', 'course-v1:TestOrg+T02+run'],
    ])
    def test_backfill_with_courses_arg_delay(self, course_ids):
        """Test called with courses arg and run in Celery worker

        See comment in the test method immediate above this one.
        """
        [CourseOverviewFactory(id=cid) for cid in course_ids]
        kwargs = {'courses': course_ids, 'use_celery': True}
        calls = [mock.call(course_id) for course_id in course_ids]

        with mock.patch(self.TASK) as mock_task:
            with mock.patch(self.TASK + '.delay') as mock_task_delay:
                call_command(self.MANAGEMENT_COMMAND, **kwargs)
                assert mock_task_delay.has_calls(calls)
                assert not mock_task.called
