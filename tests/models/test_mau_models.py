
from __future__ import absolute_import
from datetime import date
import pytest

from figures.models import CourseMauMetrics, SiteMauMetrics
from tests.factories import CourseOverviewFactory, SiteFactory


@pytest.mark.django_db
class TestCourseMauMonthlyMetrics(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = SiteFactory()
        self.course_overview = CourseOverviewFactory()

    def test_get_or_create(self):
        date_for = date(2019, 10, 29)
        rec = dict(site=self.site,
                   course_id=str(self.course_overview.id),
                   date_for=date_for,
                   mau=42)
        obj, created = CourseMauMetrics.objects.get_or_create(**rec)
        assert obj and created
        obj2, created = CourseMauMetrics.objects.get_or_create(**rec)
        assert obj2 and not created
        assert obj2 == obj
        assert obj.year == date_for.year
        assert obj.month == date_for.month

    def test_save_metrics(self):
        date_for = date(2019, 10, 29)
        course_id = str(self.course_overview.id)
        data = dict(mau=42)
        obj, created = CourseMauMetrics.save_metrics(site=self.site,
                                                     course_id=course_id,
                                                     date_for=date_for,
                                                     data=data)
        assert obj and created

        obj2, created = CourseMauMetrics.save_metrics(site=self.site,
                                                      course_id=course_id,
                                                      date_for=date_for,
                                                      data=data)
        assert obj2 and not created
        assert obj2 == obj

        data['mau'] = 104
        obj3, created = CourseMauMetrics.save_metrics(site=self.site,
                                                      course_id=course_id,
                                                      date_for=date_for,
                                                      data=data,
                                                      overwrite=True)
        assert obj3 == obj2
        assert obj3.mau == data['mau']

    def test_latest_for_course_month(self):
        date_for = date(2019, 10, 29)
        course_id = str(self.course_overview.id)
        data = dict(mau=42)
        obj = CourseMauMetrics.objects.latest_for_course_month(site=self.site,
                                                               course_id=course_id,
                                                               year=date_for.year,
                                                               month=date_for.month)
        assert not obj
        obj2, created = CourseMauMetrics.save_metrics(site=self.site,
                                                      course_id=course_id,
                                                      date_for=date_for,
                                                      data=data)

        # This is just basic. We need to test with multiple records with
        # different modified timestamps to make sure we get the latest
        obj3 = CourseMauMetrics.objects.latest_for_course_month(site=self.site,
                                                                course_id=course_id,
                                                                year=date_for.year,
                                                                month=date_for.month)
        assert obj3 and obj3 == obj2


@pytest.mark.django_db
class TestSiteMauMetrics(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.site = SiteFactory()

    def test_get_or_create(self):
        date_for = date(2019, 10, 29)
        rec = dict(site=self.site,
                   date_for=date_for,
                   mau=42)
        obj, created = SiteMauMetrics.objects.get_or_create(**rec)
        assert obj and created
        obj2, created = SiteMauMetrics.objects.get_or_create(**rec)
        assert obj2 and not created
        assert obj2 == obj
        assert obj.year == date_for.year
        assert obj.month == date_for.month

    def test_save_metrics(self):
        date_for = date(2019, 10, 29)
        data = dict(mau=42)
        obj, created = SiteMauMetrics.save_metrics(site=self.site,
                                                   date_for=date_for,
                                                   data=data)
        assert obj and created

        obj2, created = SiteMauMetrics.save_metrics(site=self.site,
                                                    date_for=date_for,
                                                    data=data)
        assert obj2 and not created
        assert obj2 == obj

        data['mau'] = 104
        obj3, created = SiteMauMetrics.save_metrics(site=self.site,
                                                    date_for=date_for,
                                                    data=data,
                                                    overwrite=True)
        assert obj3 == obj2
        assert obj3.mau == data['mau']

    def test_latest_for_site_month(self):
        date_for = date(2019, 10, 29)
        data = dict(mau=42)
        obj = SiteMauMetrics.objects.latest_for_site_month(site=self.site,
                                                           year=date_for.year,
                                                           month=date_for.month)
        assert not obj

        obj2, created = SiteMauMetrics.save_metrics(site=self.site,
                                                    date_for=date_for,
                                                    data=data)

        # This is just basic. We need to test with multiple records with
        # different modified timestamps to make sure we get the latest
        obj3 = SiteMauMetrics.objects.latest_for_site_month(site=self.site,
                                                            year=date_for.year,
                                                            month=date_for.month)
        assert obj3 and obj3 == obj2
