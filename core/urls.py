from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf.urls.static import static
from django.conf import settings
from utils.custom.admin.admin_otp_view import admin_otp_page
urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        # swagger
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
        path('api/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        # debug toolbar
        path("__debug__/", include("debug_toolbar.urls")),
        # rest framework
        # path('api-auth/', include('rest_framework.urls')),
    ]

urlpatterns += [
    # apps
    path('admin/otp-page/', admin_otp_page, name='admin_otp_page'),

    path('admin/', admin.site.urls),

    path('api/v1/users/', include('users.urls')),
    path('api/v1/sockets/', include('web_socket.urls')),
    path('api/v1/transaction/', include('transactions.urls')),
    path('api/v1/analytics/', include('analytics.urls')),
    path('api/v1/location/', include('locations.urls')),
    path('api/v1/setting/', include('user_setting.urls')),
    path('api/v1/txn-credits/', include('txn_credits.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

