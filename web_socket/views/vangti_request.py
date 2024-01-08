from rest_framework import (
    permissions,
    response,
    status,
    views,
    viewsets,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import *
from ..serializers import *
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from rest_framework.decorators import api_view, schema
from rest_framework.views import APIView


# class MessageSendAPIView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get(self, request):
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             "general", {"type": "send_info_to_user_group",
#                         "text": {"status": "done"}}
#         )
#
#         return response.Response({"status": True}, status=status.HTTP_200_OK)
#
#     def post(self, request):
#         msg = Message.objects.create(user=request.user, message={
#             "message": request.data["message"]})
#         socket_message = f"Message with id {msg.id} was created!"
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f"{request.user.id}-message", {"type": "send_last_message",
#                                            "text": socket_message}
#         )
#
#         return response.Response({"status": True}, status=status.HTTP_201_CREATED)
