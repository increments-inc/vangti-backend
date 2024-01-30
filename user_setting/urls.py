from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register('info', UserSettingViewSet, basename='user_setting')
# router.register('terms-conditions', VangtiTermsViewSet, basename='vangti_terms')


urlpatterns = [
                  # path('language/', UserSettingViewSet.as_view({"patch": "edit_language"}), name='user_edit_language'),
                  path('terms/', UserSettingViewSet.as_view({"patch": "edit_terms"}), name='user_edit_terms'),
                  # path('get/', UserSettingViewSet.as_view({"get": "get_setting"}), name='user_get_setting'),
                  # path('register/', RegistrationViewSet.as_view({"post": "post"}), name='user_registration'),

                  path('vangti-terms-conditions/', VangtiTermsViewSet.as_view({"get": "get_terms"}), name='vangti_terms_n_conditions'),

              ] + router.urls
