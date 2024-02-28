from django.utils.deprecation import MiddlewareMixin
import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken, BlacklistMixin


class JWTAccessToken(BlacklistMixin, AccessToken):
    pass


class CustomMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # access = request.headers["Authorization"].split("Bearer ")[-1]
        # print("here in middleware",  request.COOKIES,request.user, access)
        # # decoded_token =
        # JWTAccessToken(access).blacklist()
        # print("here")
        return None
