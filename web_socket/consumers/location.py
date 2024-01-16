import json
from channels.db import database_sync_to_async
from django.db import transaction
from channels.generic.websocket import AsyncWebsocketConsumer
from locations.models import UserLocation, LocationRadius
from transactions.models import Transaction

"""
{
"seeker":"phone",
"seeker_location":{
"latitude": 51,
"longitude":51
},
"provider":"phone",
"provider_location":{
"latitude": 51,
"longitude":51
}
}
{
"request":"get",
"data":{}
}
{
"request":"post",
"data":{"latitude":51,"longitude":51}
}
"""


class UserLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = self.scope.get("url_route")["kwargs"]["room_name"]

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
            return
        tr_data = await self.get_transaction(self.room_group_name)
        if transaction is None:
            return

        seeker_location = await self.get_user_location(tr_data["seeker"])
        provider_location = await self.get_user_location(tr_data["provider"])



        if receive_dict["request"]=="get":
            receive_dict = {
                "request":"response",
                "transaction_id": self.room_group_name.split("-")[0],
                "seeker": tr_data["seeker"],
                "seeker_location": seeker_location,
                "provider": tr_data["provider"],
                "provider_location": provider_location,
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send.sdpt',
                    'receive_dict': receive_dict,
                }
            )

        if receive_dict["request"]=="post":
            user = self.user.phone_number
            data = receive_dict["data"]
            if user.phone_number==tr_data["seeker"]:
                seeker_location = await self.patch_user_location(tr_data["seeker"])
            if user.phone_number==tr_data["provider"]:
                provider_location = await self.patch_user_location(tr_data["provider"])
            receive_dict = {
                "request":"response",
                "transaction_id": self.room_group_name.split("-")[0],
                "seeker": tr_data["seeker"],
                "seeker_location": seeker_location,
                "provider": tr_data["provider"],
                "provider_location": provider_location,
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send.sdpt',
                    'receive_dict': receive_dict,
                }
            )

        # receive_dict["user"] = self.scope["user"].phone_number
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'send.sdpt',
        #         'receive_dict': receive_dict,
        #         # 'user': self.scope["user"]
        #     }
        # )

    async def send_sdpt(self, event):
        receive_dict = event['receive_dict']

        await self.send(text_data=json.dumps({
            'message': receive_dict,
        }))

    @database_sync_to_async
    def get_transaction(self, room_name):
        try:
            transaction_id = room_name.split("-")[0]
            transaction = Transaction.objects.filter(id=int(transaction_id)).first()
            data  = {"seeker": transaction.seeker.phone_number, "provider": transaction.provider.phone_number}
            return data
        except:
            return None

    @database_sync_to_async
    def get_user_location(self, user_phone):
        user_phone_number = self.user.phone_number
        try:
            loc = UserLocation.objects.filter(user_phone_number=user_phone_number).first()
            data = {
                "latitude": loc.latitude,
                "longitude": loc.longitude
            }
            return data
        except:
            return

    @database_sync_to_async
    def patch_user_location(self, user, data):
        try:
            loc = UserLocation.objects.filter(user_phone_number=user).first()
            loc.latitude = data['latitude']
            loc.longitude = data['longitude']
            loc.save()
            return loc
        except:
            return
