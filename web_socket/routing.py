from django.urls import re_path,path

from .consumers import *


websocket_urlpatterns = [
    path('ws/vangti/', VangtiConsumer.as_asgi()),
    path('ws/vangti/messages/<str:room_name>/', MessagingConsumer.as_asgi()),

]
