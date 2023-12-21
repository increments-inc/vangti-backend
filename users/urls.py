from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    # simple jwt
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),




    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair2'),
    path('number_enter/', GetNumberViewSet.as_view({"post": "post"}), name='token_obtain_pair3'),
]
