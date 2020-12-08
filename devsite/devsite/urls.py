"""URL patterns includes for Figures development website
"""

from __future__ import absolute_import
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='homepage.html'), name='homepage'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^figures/', include(('figures.urls', 'figures'), namespace='figures')),
]

if settings.ENABLE_OPENAPI_DOCS:
    from rest_framework import permissions
    from drf_yasg2.views import get_schema_view
    from drf_yasg2 import openapi
    schema_view = get_schema_view(
       openapi.Info(
          title="Figures API",
          default_version='v1',
          description="Figures devsite API",
          terms_of_service="https://www.google.com/policies/terms/",
          contact=openapi.Contact(email="contact@snippets.local"),
          license=openapi.License(name="BSD License"),
       ),
       public=True,
       permission_classes=[permissions.AllowAny],
    )
    urlpatterns += [
        url(r'^api-docs(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
        url(r'^api-docs/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
        url(r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
    ]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
