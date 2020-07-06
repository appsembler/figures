"""Tests Figures enrollment dta viewset
"""

from decimal import Decimal
import pytest

import django.contrib.sites.shortcuts
from django.utils.timezone import utc
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from figures.models import LearnerCourseGradeMetrics
from figures.serializers import (
    EnrollmentMetricsSerializer,
    )

from figures.views import EnrollmentMetricsViewSet

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    LearnerCourseGradeMetricsFactory,
    OrganizationFactory,
    OrganizationCourseFactory,
    SiteFactory,
    UserFactory,
)
from tests.helpers import organizations_support_sites
from tests.views.base import BaseViewTest
from tests.views.helpers import assert_paginated

if organizations_support_sites():
    from tests.factories import UserOrganizationMappingFactory

    def map_users_to_org_site(caller, site, users):
        org = OrganizationFactory(sites=[site])
        UserOrganizationMappingFactory(user=caller,
                                       organization=org,
                                       is_amc_admin=True)
        [UserOrganizationMappingFactory(user=user,
                                        organization=org) for user in users]
        # return created objects that the test will need
        return caller


@pytest.fixture
def enrollment_test_data():
    num_courses = 2
    site = SiteFactory()
    course_overviews = [CourseOverviewFactory() for i in range(num_courses)]
    # Create a number of enrollments for each course
    enrollments = []
    for num_enroll, co in enumerate(course_overviews, 1):
        enrollments += [CourseEnrollmentFactory(
            course_id=co.id) for i in range(num_enroll)]

    # This is a convenience for the test method
    users = [enrollment.user for enrollment in enrollments]
    return dict(
        site=site,
        course_overviews=course_overviews,
        enrollments=enrollments,
        users=users,
    )


@pytest.mark.django_db
class TestEnrollmentMetricsViewSet(BaseViewTest):

    base_request_path = 'api/enrollment-metrics/'
    view_class = EnrollmentMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        if organizations_support_sites():
            settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        super(TestEnrollmentMetricsViewSet, self).setup(db)

    def check_serialized_data(self, result_rec, obj):
        fields = ['id', 'course_id', 'date_for', 'points_earned',
                  'points_possible', 'sections_worked', 
                  'sections_possible']
        expected_keys = fields + ['user', 'completed', 'progress_percent']
        assert set(result_rec.keys()) == set(expected_keys)

        for key in fields:
            obj_val = obj.__dict__[key]
            if key == 'date_for':
                obj_val = str(obj_val)
            assert result_rec[key] == obj_val
        assert result_rec['completed'] == obj.completed
        prog_pct = str(Decimal(obj.progress_percent).quantize(Decimal('.00')))
        assert result_rec['progress_percent'] == prog_pct

    def test_list_method(self, monkeypatch, enrollment_test_data):
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']

        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=users)
        else:
            caller = UserFactory(is_staff=True)

        other_site = SiteFactory()
        assert site.domain != other_site.domain
        LearnerCourseGradeMetricsFactory(site=other_site)
        lcgm = [LearnerCourseGradeMetricsFactory(site=site) for i in range(5)]

        request = APIRequestFactory().get(self.base_request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == status.HTTP_200_OK
        assert_paginated(response.data)
        results = response.data['results']
        # Check keys
        result_ids = [obj['id'] for obj in results]
        assert set(result_ids) == set([obj.id for obj in lcgm])
        # Spot check the first record
        obj = LearnerCourseGradeMetrics.objects.get(id=results[0]['id'])
        self.check_serialized_data(results[0], obj)

    def test_completions(self, monkeypatch, enrollment_test_data):
        # course_overview = sog_data['course_overview']
        site = enrollment_test_data['site']
        users = enrollment_test_data['users']
        if organizations_support_sites():
            caller = UserFactory(is_staff=True)
            map_users_to_org_site(caller=caller, site=site, users=[])
        else:
            caller = UserFactory(is_staff=True)

        expected_response = 'test response'

        # request_path = self.base_request_path + str(course_overview.id) + '/active_users/'
        request_path = self.base_request_path + '/completions/'
        request = APIRequestFactory().get(request_path)

        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
