from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    RegistrationViewSet,
    FirebasePhoneAuthView,
    UserViewSet,
    LogoutView,
)

router = DefaultRouter()
router.register(r'register', RegistrationViewSet, basename='register')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('firebase/phone-auth/', FirebasePhoneAuthView.as_view(), name='firebase_phone_auth'),
    path('deactivate/', UserViewSet.as_view({'patch': 'deactivate_user'}), name='user_deactivate'),
    path('delete/', UserViewSet.as_view({'patch': 'delete_user'}), name='user_delete'),
    path('change-pin/', UserViewSet.as_view({'patch': 'change_pin'}), name='user_change_pin'),
]
