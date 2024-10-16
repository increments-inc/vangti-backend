from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
import re
User = get_user_model()


class QueryAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            token_initial = scope["query_string"].decode("utf-8").split("=")[1]
            decoded_token = jwt.decode(token_initial, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['user_id']
            scope['user'] = await self.get_user(user_id)

            # match if user token and user room matches
            matched = re.search('/ws/vangti/request/(.+?)-room/', scope["path"])
            if matched:
                found = matched.group(1)
                if found == user_id:
                    return await self.app(scope, receive, send)

            return None
        except:
            return None

    @database_sync_to_async
    def get_user(self, user_id):
        # try:
        return User.objects.get(id=user_id)

    # @database_sync_to_async
    # def check_token_blacklist(self, token_initial, user):
    #     refresh_instance = RefreshToken(token_initial)
    #     print(refresh_instance)
    #
    #     try:
    #         for token in OutstandingToken.objects.filter(user_id=user):
    #             print("helo world")
    #             if token == token_initial:
    #                 print("token match")
    #                 pass
    #         return 0
    #     except:
    #         return
