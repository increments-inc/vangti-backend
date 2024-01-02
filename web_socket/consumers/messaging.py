import json
from channels.db import database_sync_to_async
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from ..models import SocketRoom, RoomMessages


class MessagingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        kwargs = self.scope.get("url_route")["kwargs"]
        self.user = self.scope["user"]
        self.room = await self.create_room_instance()
        self.room_group_name = f"{self.room.name}-room"
        print(self.room_group_name)
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
        print(text_data)

        if text_data:
            user_list = await self.get_user_list(text_data)
            print(user_list)
        receive_dict = text_data
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

    @database_sync_to_async
    def create_room_instance(self, room_name):
        user = self.user
        print(user)
        try:
            return Room.objects.create(seeker=user)
        except:
            return None

