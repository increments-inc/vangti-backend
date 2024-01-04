import json
from channels.db import database_sync_to_async
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from locations.models import UserLocation, LocationRadius


class VangtiConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        kwargs = self.scope.get("url_route")["kwargs"]
        # room = kwargs["user_room_name"]
        self.user = self.scope["user"]
        # self.room = await self.create_instance(room)
        self.room_group_name = f"{self.user.id}-room"
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
    def get_user_list(self, room_name):
        user = self.user
        print(user)
        try:
            return UserLocation.objects.using('location').get(user=user.id).location_radius_userlocation.user_id_list
        except:
            return

    # @database_sync_to_async
    # def insert_offer(self, text_data, client):
    #     roomname = self.scope.get("url_route")["kwargs"]["room_name"]
    #     room = RoomModel.objects.get(
    #         name=roomname
    #     )
    #     text_data = text_data.replace("{", "").replace("}", "").replace("\":", "").replace("message", "")
    #     room.offer_sdp = text_data
    #     room.offer_client = client
    #
    #     return room.save()
