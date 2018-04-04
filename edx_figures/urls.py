'''
edx-figures URL definitions
'''

from django.conf.urls import url

from . import views

urlpatterns = [

    # UI Templates
    url(r'^$', views.edx_figures_home, name='edx-figures-home'),

    # REST API
    url(r'^api/courses-index/', views.CoursesIndexView.as_view(),
        name='courses-index'),
]
