'''Tests Figures CourseDailyMetrics model

'''

import datetime
import pytest

from django.db.utils import IntegrityError

from figures.models import CourseDailyMetrics

from tests.factories import CourseDailyMetricsFactory


@pytest.mark.django_db
class TestCourseDailyMetrics(object):
    '''"Tests the CourseDailyMetrics model

    Focuses on testing CourseDailyMetrics fields and methods

    TODO: Improve testing unique constraints
    TODO: Check and test for field validators
    '''
    @pytest.fixture(autouse=True)
    def setup(self, db):
        '''Placeholder for test setup
        '''
        pass

    @pytest.mark.skip(
        reason="CourseKeyField not yet implemented in CourseDailyMetrics")
    def test_course_key(self):
        pass

    @pytest.mark.parametrize('rec', [
        dict(
            date_for=datetime.date(2018, 02, 02),
            course_id='course-v1:SomeOrg+ABC01+2121',
            defaults=dict(
                enrollment_count=11,
                active_learners_today=1,
                average_progress=0.5,
                average_days_to_complete=5,
                num_learners_completed=10
            ),
        ),
    ])
    def test_get_or_create(self, rec):
        '''Sanity check we can create the SiteDailyMetrics model

        Create a second instance the way we'll do it in the production code.
        Assert this is correct
        '''

        metrics, created = CourseDailyMetrics.objects.get_or_create(**rec)
        assert metrics and created
        metrics2, created = CourseDailyMetrics.objects.get_or_create(**rec)
        assert metrics2 and not created
        assert metrics2 == metrics

    @pytest.mark.parametrize('rec', [
        dict(
            date_for=datetime.date(2018, 02, 02),
            course_id='course-v1:SomeOrg+ABC01+2121',
            enrollment_count=11,
            active_learners_today=1,
            average_progress=0.5,
            average_days_to_complete=5,
            num_learners_completed=10
        ),
    ])
    def test_create_violates_unique(self, rec):
        '''Test CourseDailyMetrics unique constraints
        First create a model instance, then try creating with the same
        date_for and course_id. It should raise IntegrityError
        '''
        metrics = CourseDailyMetrics.objects.create(**rec)
        with pytest.raises(IntegrityError) as e_info:
            metrics = CourseDailyMetrics.objects.create(**rec)

    @pytest.mark.skip(reason='Test not yet implemented')
    def test_get_by_unique_fields(self):
        pass

    @pytest.mark.skip(reason='Test not yet implemented')
    def test_course_id_is_not_valid(self):
        '''Ensure we can only create with a valid Course ID

        and that the course_id is also not an empty string
        '''
        pass
