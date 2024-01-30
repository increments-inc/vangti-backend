import json
import time

from channels.db import database_sync_to_async
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from locations.models import UserLocation, LocationRadius
from ..fcm import send_push
from ..tasks import *
from datetime import datetime, timedelta


class VangtiConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        kwargs = self.scope.get("url_route")["kwargs"]
        self.user = self.scope["user"]
        self.room_group_name = f"dummy"
        print("all items", self.scope, self.scope["user"], kwargs, self.channel_layer)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        receive_dict = text_data
        try:
            receive_dict = json.loads(text_data)
        except:
            pass
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send.sdpt',
                'receive_dict': receive_dict,
            }
        )



    async def send_sdpt(self, event):
        receive_dict = event['receive_dict']

        await self.send(text_data=json.dumps({
            'message': receive_dict,
        }))
