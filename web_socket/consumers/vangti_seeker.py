import json
import time
from channels.db import database_sync_to_async
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from locations.models import UserLocation, LocationRadius
from ..fcm import send_push


class VangtiSeekerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        kwargs = self.scope.get("url_route")["kwargs"]
        self.user = self.scope["user"]
        room_name = self.user.phone_number.split("+")[1]
        self.room_group_name = f"{room_name}-room"
        print("all items", self.scope, self.scope["user"], kwargs, self.channel_layer, self.room_group_name)

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
            print(receive_dict, type(receive_dict))
            receive_dict["user"] = self.user.phone_number
            print(receive_dict)
        except:
            receive_dict = receive_dict + f"{self.user.phone_number}"

        if "vs" in text_data:
            await self.channel_layer.group_send(
                "8801234567891-room",
                {
                    'type': 'send.sdpt',
                    'receive_dict': receive_dict,
                }
            )
        if "vp" in text_data:
            await self.channel_layer.group_send(
                "8801234567892-room",
                {
                    'type': 'send.sdpt',
                    'receive_dict': receive_dict,
                }
            )

    async def send_sdpt(self, event):
        print(event)
        receive_dict = event['receive_dict']
        if type(receive_dict) == str:
            print("yes")
            receive_dict = json.loads(receive_dict)

        await self.send(text_data=json.dumps({
            'message': receive_dict,
            "user": self.user.phone_number
        }))

    async def send_user_push(self, user_list):
        is_affirmed = False
        for user in user_list:
            token = ""
            send_push("", "helo", token, {"user": user})
            # confirm the waiting time
            time.sleep(60)
            is_affirmed = await self.get_user_affirmation("room_name")
            if is_affirmed:
                break

        return is_affirmed

    @database_sync_to_async
    def get_user_list(self, room_name):
        user = self.user
        print(user)
        try:
            return UserLocation.objects.using('location').get(user=user.id).location_radius_userlocation.user_id_list
        except:
            return

    @database_sync_to_async
    def get_user_affirmation(self, room_name):
        user = self.user
        print(user)
        try:
            return UserLocation.objects.using('location').get(user=user.id).location_radius_userlocation.user_id_list
        except:
            return
