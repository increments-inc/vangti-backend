from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
import jwt
from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


@database_sync_to_async
def check_token_blacklist(token_initial, user):
    try:
        for token in OutstandingToken.objects.filter(user_id=user):
            # print("common")
            if token == token_initial:
                print("here")

        return 0
    except:
        return

class QueryAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        token_initial = scope["query_string"].decode("utf-8").split("=")[1]
        # token = await check_token_blacklist(token_initial)
        # print(token)
        decoded_token = jwt.decode(token_initial, settings.SECRET_KEY, algorithms=['HS256'])
        # print(decoded_token, "sdsdfsfdfsd")
        user_id = decoded_token['user_id']
        scope['user'] = await get_user(user_id)
        # token = await check_token_blacklist(token_initial, user_id)

        return await self.app(scope, receive, send)
