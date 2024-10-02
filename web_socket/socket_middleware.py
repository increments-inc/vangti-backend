from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

User = get_user_model()


@database_sync_to_async
def check_token_blacklist(token_initial, user):
    try:
        for token in OutstandingToken.objects.filter(user_id=user):
            if token == token_initial:
                pass
        return 0
    except:
        return


class QueryAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            token_initial = scope["query_string"].decode("utf-8").split("=")[1]
            decoded_token = jwt.decode(token_initial, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['user_id']
            scope['user'] = await self.get_user(user_id)
            return await self.app(scope, receive, send)
        except:
            return None

    @database_sync_to_async
    def get_user(self, user_id):
        # try:
        return User.objects.get(id=user_id)
