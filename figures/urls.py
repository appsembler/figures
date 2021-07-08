'''
Figures URL definitions
'''

from __future__ import absolute_import
from django import VERSION as DJANGO_VERSION
from django.conf.urls import include, url
from rest_framework import routers

from figures import views

app_name = 'figures'

router = routers.DefaultRouter()

router.register(
    r'course-daily-metrics',
    views.CourseDailyMetricsViewSet,
    base_name='course-daily-metrics')

router.register(
    r'site-daily-metrics',
    views.SiteDailyMetricsViewSet,
    base_name='site-daily-metrics')

router.register(
    r'course-monthly-metrics',
    views.CourseMonthlyMetricsViewSet,
    base_name='course-monthly-metrics')

router.register(
    r'site-monthly-metrics',
    views.SiteMonthlyMetricsViewSet,
    base_name='site-monthly-metrics')

router.register(
    r'course-mau-metrics',
    views.CourseMauMetricsViewSet,
    base_name='course-mau-metrics')

router.register(
    r'site-mau-metrics',
    views.SiteMauMetricsViewSet,
    base_name='site-mau-metrics')

router.register(
    r'course-mau-live-metrics',
    views.CourseMauLiveMetricsViewSet,
    base_name='course-mau-live-metrics')

router.register(
    r'site-mau-live-metrics',
    views.SiteMauLiveMetricsViewSet,
    base_name='site-mau-live-metrics')


router.register(
    r'admin/sites',
    views.SiteViewSet,
    base_name='sites')

# Wrappers around edx-platform models
router.register(
    r'course-enrollments',
    views.CourseEnrollmentViewSet,
    base_name='course-enrollments')


#
# For the front end UI
#


router.register(
    r'courses-index',
    views.CoursesIndexViewSet,
    base_name='courses-index')

router.register(
    r'courses-general',
    views.GeneralCourseDataViewSet,
    base_name='courses-general')

router.register(
    r'courses-detail',
    views.CourseDetailsViewSet,
    base_name='courses-detail')

router.register(
    r'users-general',
    views.GeneralUserDataViewSet,
    base_name='users-general')

router.register(
    r'users-detail',
    views.LearnerDetailsViewSet,
    base_name='users-detail')

# TODO: Consider changing this path to be 'users' or 'users/summary'
# So that all user data fall under the same root path

router.register(
    r'user-index',
    views.UserIndexViewSet,
    base_name='user-index')


# New endpoints in development (unstable)
# Unstable here means the code is subject to change without notice

router.register(
    r'enrollment-metrics',
    views.EnrollmentMetricsViewSet,
    base_name='enrollment-metrics')

router.register(
    r'learner-metrics-v1',
    views.LearnerMetricsViewSetV1,
    base_name='learner-metrics-v1')

router.register(
    r'learner-metrics',
    views.LearnerMetricsViewSetV2,
    base_name='learner-metrics')

urlpatterns = [

    # UI Templates
    url(r'^$', views.figures_home, name='figures-home'),

    # Non-router API endpoints
    url(r'^api/general-site-metrics', views.GeneralSiteMetricsView.as_view(),
        name='general-site-metrics'),
]

# Include router endpoints
# Breaking changes between Django 1.8 and Django 2.0 so we do this

if DJANGO_VERSION[0] < 2:
    urlpatterns.append(url(r'^api/', include(router.urls, namespace='api')))
else:
    urlpatterns.append(url(r'^api/', include((router.urls, 'api'), namespace='api')))

# Reroute all unmatched traffic to Figures main UI page
urlpatterns.append(url(r'^(?:.*)/?$', views.figures_home, name='router-catch-all'))
