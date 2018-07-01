'''
Figures URL definitions
'''

from django.conf.urls import include, url
from rest_framework import routers
from django.views.generic.base import RedirectView

from . import views

router = routers.DefaultRouter()

router.register(
    r'site-daily-metrics',
    views.SiteDailyMetricsViewSet,
    base_name='site-daily-metrics')

router.register(
    r'course-daily-metrics',
    views.CourseDailyMetricsViewSet,
    base_name='course-daily-metrics')


## Wrappers around edx-platform models
router.register(
    r'course-enrollments',
    views.CourseEnrollmentViewSet,
    base_name='course-enrollments')


##
## For the front end UI
##

router.register(
    r'courses/general',
    views.GeneralCourseDataViewSet,
    base_name='general-courses')

router.register(
    r'users/general',
    views.GeneralUserDataViewSet,
    base_name='general-users')


urlpatterns = [

    # UI Templates
    url(r'^$', views.figures_home, name='figures-home'),

    # REST API
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/courses-index/', views.CoursesIndexView.as_view(),
        name='courses-index'),
    url(r'^api/user-index/', views.UserIndexView.as_view(), name='user-index'),
    url(r'^api/general-site-metrics', views.GeneralSiteMetricsView.as_view(),
        name='general-site-metrics'),
    url('', RedirectView.as_view(pattern_name='figures-home'), name="catch-all")
]
