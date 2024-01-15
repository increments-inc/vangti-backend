from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
import jwt
from django.conf import settings

User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class QueryAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        print()
        token = scope["query_string"].decode("utf-8").split("=")[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decoded_token['user_id']
        scope['user'] = await get_user(user_id)

        return await self.app(scope, receive, send)
