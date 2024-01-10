from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # debug toolbar
    path("__debug__/", include("debug_toolbar.urls")),

    # rest framework
    # path('api-auth/', include('rest_framework.urls')),




    # apps
    path('admin/', admin.site.urls),

    path('api/users/', include('users.urls')),
    path('api/sockets/', include('web_socket.urls')),
    path('api/transaction/', include('transactions.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/location/', include('locations.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

