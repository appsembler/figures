'''Tests Figures CourseDailyMetrics model


TODO:
* Test cascade delete behavior
* Test default site is added if not specified in construction
'''

from __future__ import absolute_import
import datetime
from decimal import Decimal
import pytest

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from opaque_keys.edx.locator import CourseLocator

from figures.models import CourseDailyMetrics

from tests.factories import (
    CourseDailyMetricsFactory,
    CourseOverviewFactory,
    SiteFactory,
)


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
        self.site = Site.objects.first()

    @pytest.mark.skip(
        reason="CourseKeyField not yet implemented in CourseDailyMetrics")
    def test_course_key(self):
        pass

    def test_get_or_create(self):
        '''Sanity check we can create the SiteDailyMetrics model

        Create a second instance the way we'll do it in the production code.
        Assert this is correct
        '''
        rec = dict(
            site=self.site,
            date_for=datetime.date(2018, 2, 2),
            course_id='course-v1:SomeOrg+ABC01+2121',
            defaults=dict(
                enrollment_count=11,
                active_learners_today=1,
                average_progress=0.5,
                average_days_to_complete=5,
                num_learners_completed=10
            ),
        )
        metrics, created = CourseDailyMetrics.objects.get_or_create(**rec)
        assert metrics and created
        metrics2, created = CourseDailyMetrics.objects.get_or_create(**rec)
        assert metrics2 and not created
        assert metrics2 == metrics

    def test_update_or_create(self):
        course_id = "course-v1:certs-appsembler+001+2019"
        date_for = "2019-01-30"
        data = {
            'average_progress': 0.1,
            'num_learners_completed': 2,
            'enrollment_count': 3,
            'average_days_to_complete': 0.0,
            'course_id': CourseLocator(u'certs-appsembler', u'001', u'2019', None, None),
            'date_for': date_for,
            'active_learners_today': 0}

        cdm, created = CourseDailyMetrics.objects.update_or_create(
            course_id=course_id,
            site=self.site,
            date_for=date_for,
            defaults=dict(
                enrollment_count=data['enrollment_count'],
                active_learners_today=data['active_learners_today'],
                average_progress=data['average_progress'],
                average_days_to_complete=1,  # int(round(data['average_days_to_complete'])),
                num_learners_completed=0,  # data['num_learners_completed'],
            )
        )

    @pytest.mark.parametrize('average_progress', [-1.0, -0.01, 1.01])
    def test_with_invalid_average_progress(self, average_progress):
        """
        Apparently Django models don't validate automatically on save
        """
        assert average_progress < 0 or average_progress > 1
        rec = dict(
            site=self.site,
            date_for=datetime.date(2018, 2, 2),
            course_id='course-v1:SomeOrg+ABC01+2121',
            enrollment_count=11,
            active_learners_today=1,
            average_progress=average_progress,
            average_days_to_complete=5,
            num_learners_completed=10
        )
        obj = CourseDailyMetrics(**rec)
        with pytest.raises(ValidationError) as execinfo:
            obj.clean_fields()

        assert 'average_progress' in execinfo.value.message_dict

    @pytest.mark.skip('fails')
    @pytest.mark.parametrize('average_progress',
        [0.0, 0.01, 0.5, 0.99, 1.0])
    def test_with_valid_average_progress(self, average_progress):
        """
        Average progress must be between 0.0 and 1.0 inclusive and no more than 2 decimal places
        """

        rec =  dict(
            site=self.site,
            date_for=datetime.date(2018, 2, 2),
            course_id='course-v1:SomeOrg+ABC01+2121',
            enrollment_count=11,
            active_learners_today=1,
            average_progress=str(average_progress),
            average_days_to_complete=5,
            num_learners_completed=10
        )
        metrics = CourseDailyMetrics.objects.create(**rec)
        assert metrics.average_progress == average_progress
        metrics.clean_fields()

    @pytest.mark.parametrize('average_progress',
        [0.0, 0.01, 0.5, 0.99, 1.0])
    def test_with_valid_average_progress_2(self, average_progress):
        """
        Average progress must be between 0.0 and 1.0 inclusive and no more than 2 decimal places
        """

        rec =  dict(
            site=self.site,
            date_for=datetime.date(2018, 2, 2),
            course_id='course-v1:SomeOrg+ABC01+2121',
            defaults=dict(
                enrollment_count=11,
                active_learners_today=1,
                average_progress=str(average_progress),
                average_days_to_complete=5,
                num_learners_completed=10,
            )
        )
        cdm, created = CourseDailyMetrics.objects.update_or_create(**rec)
        cdm.save()

        assert cdm.average_progress == str(average_progress)
        cdm.clean_fields()

    def test_site(self):
        """
        Tests expected CourseDailyMetrics behavior for working with a Site
        """
        assert Site.objects.count() == 1

        rec_data = dict(
            site=self.site,
            date_for=datetime.date(2018, 2, 2),
            enrollment_count=11,
            active_learners_today=1,
            average_progress=0.5,
            average_days_to_complete=5,
            num_learners_completed=10
        )
        rec = rec_data.copy()
        rec['course_id'] = 'course-v1:SomeOrg+ABC01+2121'
        obj = CourseDailyMetrics.objects.create(**rec)
        assert obj.site == Site.objects.first()
        rec['course_id'] = 'course-v1:AlphaOrg+ABC01+2121'
        alpha_site = SiteFactory(domain='alpha.example.com', name='Alpha')
        assert Site.objects.count() == 2
        rec['site'] = alpha_site
        obj2 = CourseDailyMetrics.objects.create(**rec)
        assert obj2.site == alpha_site

        # Test cascade delete
        assert CourseDailyMetrics.objects.count() == 2
        alpha_site.delete()
        assert CourseDailyMetrics.objects.count() == 1
        # Verify we deleted the correct metrics object
        assert obj == CourseDailyMetrics.objects.first()

    def test_create_violates_unique(self, ):
        '''Test CourseDailyMetrics unique constraints
        First create a model instance, then try creating with the same
        date_for and course_id. It should raise IntegrityError
        '''

        rec = dict(
            site=self.site,
            date_for=datetime.date(2018, 2, 2),
            course_id='course-v1:SomeOrg+ABC01+2121',
            enrollment_count=11,
            active_learners_today=1,
            average_progress=0.5,
            average_days_to_complete=5,
            num_learners_completed=10
        )
        metrics = CourseDailyMetrics.objects.create(**rec)
        with pytest.raises(IntegrityError) as e_info:
            metrics = CourseDailyMetrics.objects.create(**rec)
            assert e_info.value.message.startswith('UNIQUE constraint failed')

    @pytest.mark.skip(reason='Test not yet implemented')
    def test_get_by_unique_fields(self):
        pass

    @pytest.mark.skip(reason='Test not yet implemented')
    def test_course_id_is_not_valid(self):
        '''Ensure we can only create with a valid Course ID

        and that the course_id is also not an empty string
        '''
        pass

    def test_latest_previous_record(self):
        course_overview = CourseOverviewFactory()

        # Create a set of records with non-continuous dates
        dates = [
            datetime.date(2019, 10, 1),
            datetime.date(2019, 10, 2),
            datetime.date(2019, 10, 5),
            datetime.date(2019, 10, 29),
            datetime.date(2019, 11, 3),
        ]
        for rec_date in dates:
            cdms = CourseDailyMetricsFactory(site=self.site,
                                             course_id = course_overview.id,
                                             date_for=rec_date)

        rec = CourseDailyMetrics.latest_previous_record(
            site=self.site,
            course_id=course_overview.id)
        assert rec.date_for == dates[-1]

        rec2 = CourseDailyMetrics.latest_previous_record(
            site=self.site,
            course_id=course_overview.id,
            date_for=dates[-1])
        assert rec2.date_for == dates[-2]

        rec3 = CourseDailyMetrics.latest_previous_record(
            site=self.site,
            course_id=course_overview.id,
            date_for=dates[0])
        assert not rec3
