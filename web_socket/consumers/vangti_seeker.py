import json
import time
from channels.db import database_sync_to_async
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from locations.models import UserLocation, LocationRadius
from transactions.models import TransactionRequest
from users.models import User
from ..fcm import send_push
from django.core.cache import cache
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

# reference json data to be sent
"""
{
    "seeker": "user_phone",
    "amount": 1000,
    "preferred": "100,20",
    "request_status":"PENDING",
    "provider": null
}

# cache
user
provider_list

"""


class VangtiSeekerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        kwargs = self.scope.get("url_route")["kwargs"]
        self.user = self.scope["user"]
        room_name = self.user.phone_number.split("+")[-1]
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
        user = self.scope["user"]
        receive_dict = text_data

        try:
            receive_dict = json.loads(text_data)
            receive_dict["user"] = self.user.phone_number
        except:
            # not recommended
            receive_dict = receive_dict + f"""{self.user.phone_number}"""

        # send out request
        if (
                receive_dict["seeker"] == self.user.phone_number and
                receive_dict["request"] == "PENDING"
        ):
            user_list = await self.get_user_list(receive_dict)
            print(user_list)
            cache.set(receive_dict["seeker"], user_list, timeout=None)
            # print(cache.get(f"{user.phone_number}"))
            send_user = user_list[0].split("+")[-1]
            receive_dict["provider"] = user_list[0]
            await self.channel_layer.group_send(
                f"{send_user}-room",
                {
                    'type': 'send_to_receiver_data',
                    'receive_dict': receive_dict,
                }
            )

        # reject request
        if (
                receive_dict["request"] == "reject" and
                receive_dict["provider"] == self.user.phone_number
        ):
            room = receive_dict["seeker"].split("+")[-1]
            seeker = receive_dict["seeker"]
            user_list = cache.get(receive_dict["seeker"])
            if user_list[0] == receive_dict["provider"]:
                user_list.pop(0)
                print(user_list)
                cache.set(receive_dict["seeker"], user_list)
            if len(user_list) != 0:
                send_user = user_list[0].split("+")[-1]
                receive_dict["provider"] = user_list[0]

                await self.channel_layer.group_send(
                    f"{send_user}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )
            else:
                room_seeker = receive_dict["seeker"].split("+")[-1]
                await self.channel_layer.group_send(
                    f"{room_seeker}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': {"message": "no user left"},
                    }
                )

        # accept request
        if (
                # receive_dict["seeker"] == self.user.phone_number and
                receive_dict["request"] == "accept" and
                receive_dict["provider"] == self.user.phone_number
        ):
            room_seeker = receive_dict["seeker"].split("+")[-1]
            room_provider = receive_dict["provider"].split("+")[-1]

            provider = await self.update_request_instance(receive_dict["seeker"], receive_dict["provider"])
            if provider.provider.phone_number == receive_dict["provider"]:
                await self.channel_layer.group_send(
                    f"{room_seeker}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )
                await self.channel_layer.group_send(
                    f"{room_provider}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': {"message": "accepted ok"},
                    }
                )
                # cache.delete(receive_dict["seeker"])
            # await self.disconnect(1000)

    async def send_to_receiver_data(self, event):
        receive_dict = event['receive_dict']
        if type(receive_dict) == str:
            receive_dict = json.loads(receive_dict)

        await self.send(text_data=json.dumps({
            'message': receive_dict,
            "user": self.user.phone_number
        }))

    # send fcm
    # async def send_user_push(self, user_list):
    #     is_affirmed = False
    #     for user in user_list:
    #         token = ""
    #         send_push("", "helo", token, {"user": user})
    #         # confirm the waiting time
    #         time.sleep(60)
    #         is_affirmed = await self.get_user_affirmation("room_name")
    #         if is_affirmed:
    #             break
    #     return is_affirmed

    @database_sync_to_async
    def get_user_list(self, room_name):
        user = self.user
        try:
            center = UserLocation.objects.using('location').get(user=user.id).centre
            radius = 10000
            user_provider_list = list(User.objects.filter(user_mode__is_provider=True).values_list('id', flat=True))
            # user_list = UserLocation.objects.using('location').get(user=user.id).location_radius_userlocation.user_id_list
            # user_list = UserLocation.objects.using('location').get(user=user.id)
            user_list = list(UserLocation.objects.using('location').filter(
                user__in=user_provider_list,
                centre__distance_lte=(center, Distance(km=radius))
            ).values_list("user_phone_number", flat=True))

            return user_list
        except:
            return

    @database_sync_to_async
    def update_request_instance(self, seeker, provider):
        provider = User.objects.get(phone_number=provider)
        try:
            t_req = TransactionRequest.objects.get(seeker__phone_number=seeker)
            t_req.provider = provider
            t_req.save()
            return t_req
        except:
            return

    # @database_sync_to_async
    # def update_request_instance(self, seeker, provider):
    #     provider = User.objects.get(phone_number=provider)
    #     try:
    #         return TransactionRequest.objects.get(seeker__phone_number=seeker)
    #     except:
    #         return
    #
    # async def text_accept(self, event):
    #     receive_dict = event['receive_dict']
    #     if type(receive_dict) == str:
    #         receive_dict = json.loads(receive_dict)
    #
    #     await self.send(text_data=json.dumps({
    #         'message': receive_dict,
    #         "user": self.user.phone_number
    #     }))
    # async def text_reject(self, event):
    #     receive_dict = event['receive_dict']
    #     if type(receive_dict) == str:
    #         receive_dict = json.loads(receive_dict)
    #
    #     await self.send(text_data=json.dumps({
    #         'message': receive_dict,
    #         "user": self.user.phone_number
    #     }))
    # async def text_pending(self, event):
    #     receive_dict = event['receive_dict']
    #     if type(receive_dict) == str:
    #         receive_dict = json.loads(receive_dict)
    #
    #     await self.send(text_data=json.dumps({
    #         'message': receive_dict,
    #         "user": self.user.phone_number
    #     }))
