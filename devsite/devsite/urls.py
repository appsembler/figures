'''
URL patterns includes for edx-figures devsite 
'''

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='homepage.html'), name='homepage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^edx-figures/', include('edx_figures.urls', namespace='edx-figures')),
]
