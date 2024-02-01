import json
import time
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from django.core.cache import cache
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction
from asgiref.sync import async_to_sync, sync_to_async
from datetime import datetime, timedelta
from locations.models import UserLocation, LocationRadius
from transactions.models import TransactionRequest
from users.models import User
from ..fcm import send_push
from ..tasks import *


class InterruptExecution(Exception):
    def __init__(self, message="Interrupt Execution"):
        self.message = message
        super().__init__(self.message)


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
        print(text_data, user)
        try:
            receive_dict = json.loads(text_data)
            receive_dict["user"] = self.user.phone_number
        except:
            return
        # send out request (seeker end)
        if (
                receive_dict["seeker"] == self.user.phone_number and
                receive_dict["request"] == "POST" and
                receive_dict["status"] == "PENDING" and
                receive_dict["provider"] is None
        ):
            print("post pending none")
            user_list = await self.get_user_list(receive_dict)
            print(user_list)
            cache.set(receive_dict["seeker"], user_list, timeout=None)
            # print(cache.get(f"{user.phone_number}"))
            send_user = user_list[0].split("+")[-1]
            receive_dict["provider"] = user_list[0]
            await self.channel_layer.group_send(
                f"{send_user}-room",
                {
                    'type': 'send_pending_data',
                    'receive_dict': receive_dict,
                }
            )



        # reject request
        if (
                receive_dict["provider"] == self.user.phone_number and
                receive_dict["request"] == "RESPONSE" and
                receive_dict["status"] == "REJECTED"
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
                receive_dict["request"] = "POST"
                receive_dict["status"] = "PENDING"
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
                        'receive_dict': {"error": "no user left"},
                    }
                )

        # accept request
        if (
                receive_dict["provider"] == self.user.phone_number and
                receive_dict["request"] == "RESPONSE" and
                receive_dict["status"] == "ACCEPTED"
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

    async def send_to_receiver_data(self, event):
        receive_dict = event['receive_dict']
        if type(receive_dict) == str:
            receive_dict = json.loads(receive_dict)

        await self.send(text_data=json.dumps({
            'message': receive_dict,
            "user": self.user.phone_number
        }))

    async def send_pending_data(self, event):
        receive_dict = event['receive_dict']
        if type(receive_dict) == str:
            receive_dict = json.loads(receive_dict)

        await self.send(text_data=json.dumps({
            'message': receive_dict,
            "user": self.user.phone_number
        }))

    async def auto_reject(self):
        time.sleep(10)
        await self.channel_layer.group_send(
            "8801234567891-room",
            {
                'type': 'send_data',
                'receive_dict': {"message": "accepted ok"},
            }
        )

    async def send_data(self, event):
        print("dfsdf")
        receive_dict = event['receive_dict']
        if type(receive_dict) == str:
            receive_dict = json.loads(receive_dict)

        await self.send(text_data=json.dumps({
            'message': receive_dict,
            # "user": self.user.phone_number
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
            user_location_list = list(
                UserLocation.objects.using('location').filter(
                    centre__distance_lte=(center, Distance(km=radius))
                ).values_list(
                    "user", flat=True
                )
            )
            user_provider_list = list(
                User.objects.filter(
                    is_superuser=False,
                    id__in=user_location_list,
                    user_mode__is_provider=True
                ).order_by(
                    "-userrating_user__rating"
                ).values_list(
                    'phone_number', flat=True
                )
            )
            return user_provider_list
        except:
            return

    @database_sync_to_async
    def update_request_instance(self, seeker, provider):
        provider = User.objects.get(phone_number=provider)
        try:
            t_req = TransactionRequest.objects.get(seeker__phone_number=seeker)
            t_req.provider = provider
            t_req.status="ACCEPTED"
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

    async def some_long_running_task(self, start_time):
        try:
            while datetime.now() < start_time + timedelta(seconds=30):
                pass
        except InterruptExecution:
            await self.channel_layer.group_send(
                "8801234567891-room",
                {
                    'type': 'send_data',
                    'receive_dict': {"message": "accepted no ok"},
                }
            )

    async def interrupt_task(self):
        # When you want to interrupt the task
        raise InterruptExecution("Stop the task")
