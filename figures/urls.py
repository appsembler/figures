'''
Figures URL definitions
'''

from django.conf.urls import include, url
from rest_framework import routers

from figures import views

router = routers.DefaultRouter()

router.register(
    r'site-daily-metrics',
    views.SiteDailyMetricsViewSet,
    base_name='site-daily-metrics')

router.register(
    r'course-daily-metrics',
    views.CourseDailyMetricsViewSet,
    base_name='course-daily-metrics')


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
    r'courses/general',
    views.GeneralCourseDataViewSet,
    base_name='courses-general')

router.register(
    r'courses/detail',
    views.CourseDetailsViewSet,
    base_name='courses-detail')

router.register(
    r'users/general',
    views.GeneralUserDataViewSet,
    base_name='users-general')

router.register(
    r'users/detail',
    views.LearnerDetailsViewSet,
    base_name='users-detail')


# TODO: Consider changing this path to be 'users' or 'users/summary'
# So that all user data fall under the same root path

router.register(
    r'user-index',
    views.UserIndexViewSet,
    base_name='user-index')


urlpatterns = [

    # UI Templates
    url(r'^$', views.figures_home, name='figures-home'),

    # REST API
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/general-site-metrics', views.GeneralSiteMetricsView.as_view(),
        name='general-site-metrics'),
    url(r'^(?:.*)/?$', views.figures_home, name='router-catch-all')
]
