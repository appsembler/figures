'''
edx-figures URL definitions
'''

from django.conf.urls import include, url
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(
    r'site-daily-metrics',
    views.SiteDailyMetricsViewSet,
    base_name='site-daily-metrics')


urlpatterns = [

    # UI Templates
    url(r'^$', views.edx_figures_home, name='edx-figures-home'),

    # REST API
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/courses-index/', views.CoursesIndexView.as_view(),
        name='courses-index'),
    url(r'^api/user-index/', views.UserIndexView.as_view(), name='user-index'),
]
