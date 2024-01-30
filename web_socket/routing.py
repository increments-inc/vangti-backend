from django.urls import re_path,path

from .consumers import *


websocket_urlpatterns = [
    # path('ws/vangti/<str:room_name>/', VangtiConsumer.as_asgi()),
    path('ws/vangti/messages/<str:room_name>/', TransactionMessageConsumer.as_asgi()),
    path('ws/vangti/location/<str:room_name>/', UserLocationConsumer.as_asgi()),
    path('ws/vangti/request/<str:room_name>/', VangtiSeekerConsumer.as_asgi()),
    # path('ws/vangti/provider/<str:room_name>/', VangtiProviderConsumer.as_asgi()),

]
