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



    # registration
    path('login/', CustomTokenObtainPairView.as_view(), name='user_login'),
    path('register/', RegistrationViewSet.as_view({"post": "post"}), name='user_registration'),
    path('set-pin/', RegistrationViewSet.as_view({"post": "set_pin"}), name='user_set_pin'),
    path('enter-phone-number/', GetNumberViewSet.as_view({"post": "post"}), name='user_number_enter'),
]
