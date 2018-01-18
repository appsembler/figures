
from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'$', views.edx_figures_home, name='edx-figures-home'),
]

