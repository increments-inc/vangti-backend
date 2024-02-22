from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# router.register('document', UserKYCDocumentViewSet, basename='user_documents')
# kyc submit
# router.register('submit-kyc-info', VerifiedUsersViewSet, basename='user_submit_kyc')
router.register('firebase-token', UserFirebaseTokenViewSet, basename='user_firebase_token')
# router.register('info', UserInformationViewSet, basename='user_information')


urlpatterns = [
                  # simple jwt
                  # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
                  path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

                  # registration
                  path('login/', CustomTokenObtainPairView.as_view(), name='user_login'),
                  path('enter-otp/', RegistrationViewSet.as_view({"post": "post"}), name='user_registration'),
                  path('enter-pin/', RegistrationViewSet.as_view({"post": "set_pin"}), name='user_set_pin'),
                  # path('set-pin-token/', UserPinViewSet.as_view({"post": "set_pin"}), name='user_set_pin_token'),
                  path('enter-phone-number/', GetNumberViewSet.as_view({"post": "post"}), name='user_number_enter'),

                  # logout
                  path('logout/', LogoutView.as_view(), name='user_logout'),

                  # reset pin----- is it needed?
                  # path('reset-pin/', UserViewSet.as_view({"patch": "reset_pin"}), name='user_reset_pin'),

                  # user account deletion
                  path('deactivate/', UserViewSet.as_view({"patch": "deactivate_user"}), name='user_deactivate'),
                  path('delete/', UserViewSet.as_view({"patch": "delete_user"}), name='user_delete'),

                  # user profile
                  path('change-pin/', UserViewSet.as_view({"patch": "change_pin"}), name='user_change_pin'),
                  path('profile-change/', UserInformationViewSet.as_view({"patch": "change_profile"}), name='user_change_profile'),
                  path('profile-get/', UserInformationViewSet.as_view({"get": "user_info"}), name='user_user_info'),

                  # path('phone-register/', PhoneUserViewSet.as_view({"post": "phone_register"}), name='user_phone_registration'),

                  # KYC/NID
                  # kyc/nid
                  # path('nid-add/', UserNidInformationViewSet.as_view({"post": "add_nid"}), name='user_add_nid'),
                  # path('nid-front-add/', UserNidInformationViewSet.as_view({"patch": "nid_front_add"}), name='user_nid_front_add'),
                  # path('nid-back-add/', UserNidInformationViewSet.as_view({"patch": "nid_back_add"}), name='user_nid_back_add'),
                  # path('nid-photo-add/', UserNidInformationViewSet.as_view({"patch": "nid_photo_add"}), name='user_photo_add'),
                  # path('nid-signature-add/', UserNidInformationViewSet.as_view({"patch": "nid_signature_add"}), name='user_signature_add'),
                  #
                  # path('nid-update/', UserNidInformationViewSet.as_view({"patch": "update_nid"}),
                  #      name='user_update_nid'),
                  # path('nid-get/', UserNidInformationViewSet.as_view({"get": "retrieve"}),
                  #      name='user_retrieve_nid'),
                  #
                  # path('kyc-add/', UserKYCInformationViewSet.as_view({"post": "add_kyc_info"}),
                  #      name='user_add_kyc_info'),
                  # path('kyc-update/', UserKYCInformationViewSet.as_view({"patch": "update_kyc_information"}),
                  #      name='user_update_kyc_information'),

              ] + router.urls
