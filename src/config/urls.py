from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


api_urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('payments/', include('payments.urls')),
]

urlpatterns = [
    path('management/admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns)),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(title='Dinero API documentation', default_version='v1'),
        public=True,
        permission_classes=(permissions.AllowAny,))

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    ]
