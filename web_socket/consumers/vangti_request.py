import hashlib
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
from transactions.models import TransactionRequest, Transaction
from users.models import User
from ..fcm import send_push
from ..tasks import *
from ..models import TransactionMessages
from django.conf import settings
import blurhash


def get_hash(picture_url):
    with open(picture_url[1:], 'rb') as image_file:
        hash = blurhash.encode(image_file, x_components=4, y_components=3)
    return hash


class InterruptExecution(Exception):
    def __init__(self, message="Interrupt Execution"):
        self.message = message
        super().__init__(self.message)


class VangtiRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        kwargs = self.scope.get("url_route")["kwargs"]
        self.user = self.scope["user"]
        room_name = self.user.id

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
        print(text_data, user.id)
        try:
            receive_dict = json.loads(text_data)
            # receive_dict["user"] = self.user.phone_number
        except:
            return
        # send out request (seeker end)
        if (
                receive_dict["data"]["seeker"] == str(self.user.id) and
                receive_dict["request"] == "TRANSACTION" and
                receive_dict["status"] == "PENDING" and
                receive_dict["data"]["provider"] is None
        ):
            print("post pending none")
            user_list = await self.get_user_list(receive_dict)
            print(user_list)
            # cache set
            cache.set(
                receive_dict["data"]["seeker"],
                user_list,
                timeout=None
            )
            # print(cache.get(f"{user.phone_number}"))
            # send_user = user_list[0].split("+")[-1]
            print("here")
            send_user = user_list[0]

            receive_dict["data"]["provider"] = user_list[0]
            receive_dict["data"]["seeker_info"] = await self.get_seeker_info(receive_dict["data"]["seeker"])
            print("final", receive_dict)
            await self.channel_layer.group_send(
                f"{send_user}-room",
                {
                    'type': 'send_pending_data',
                    'receive_dict': receive_dict,
                }
            )

        # reject request
        if (
                receive_dict["data"]["provider"] == str(self.user.id) and
                receive_dict["request"] == "TRANSACTION" and
                receive_dict["status"] == "REJECTED"
        ):
            # room = receive_dict["seeker"].split("+")[-1]
            room = receive_dict["data"]["seeker"]

            seeker = receive_dict["data"]["seeker"]
            user_list = cache.get(receive_dict["data"]["seeker"])
            if user_list[0] == receive_dict["data"]["provider"]:
                user_list.pop(0)
                print(user_list)
                cache.set(receive_dict["data"]["seeker"], user_list)
            if len(user_list) != 0:
                # send_user = user_list[0].split("+")[-1]
                send_user = user_list[0]

                receive_dict["data"]["provider"] = user_list[0]
                # receive_dict["request"] = "POST"
                receive_dict["status"] = "PENDING"
                await self.channel_layer.group_send(
                    f"{send_user}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )
            else:
                # user check!!!!!!
                # room_seeker = receive_dict["seeker"].split("+")[-1]
                room_seeker = receive_dict["data"]["seeker"]
                receive_dict["status"] = "NO_PROVIDER"

                await self.channel_layer.group_send(
                    f"{room_seeker}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )

        # accept request
        if (
                receive_dict["data"]["provider"] == str(self.user.id) and
                receive_dict["request"] == "TRANSACTION" and
                receive_dict["status"] == "ACCEPTED"
        ):
            # room_seeker = receive_dict["seeker"].split("+")[-1]
            # room_provider = receive_dict["provider"].split("+")[-1]

            room_seeker = receive_dict["data"]["seeker"]
            room_provider = receive_dict["data"]["provider"]

            transaction_id = await self.update_request_instance(receive_dict)
            print("here", transaction)

            receive_dict["status"] = "ON_GOING_TRANSACTION"
            receive_dict["data"]["transaction_id"] = transaction_id

            if receive_dict["data"]["provider"]:
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
                        'receive_dict': receive_dict,
                    }
                )
                # cache.delete(receive_dict["seeker"])

        # location
        if (
                (receive_dict["data"]["seeker"] == str(self.user.id)
                 or receive_dict["data"]["provider"] == str(self.user.id))
                and
                receive_dict["request"] == "LOCATION" and
                receive_dict["status"] == "ON_GOING_TRANSACTION"
        ):
            # room_seeker = receive_dict["seeker"].split("+")[-1]
            # room_provider = receive_dict["provider"].split("+")[-1]

            room_seeker = receive_dict["data"]["seeker"]
            room_provider = receive_dict["data"]["provider"]

            receive_dict["data"]["seeker_location"] = await self.get_user_location(receive_dict["data"]["seeker"])
            receive_dict["data"]["provider_location"] = await self.get_user_location(receive_dict["data"]["provider"])
            receive_dict["data"]["direction"] = await self.get_direction(receive_dict["data"]["seeker"],
                                                                         receive_dict["data"]["provider"])

            if receive_dict["data"]["provider"]:
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
                        'receive_dict': receive_dict,
                    }
                )
        # message
        if (
                (receive_dict["data"]["seeker"] == str(self.user.id)
                 or receive_dict["data"]["provider"] == str(self.user.id))
                and
                receive_dict["request"] == "MESSAGE" and
                receive_dict["status"] == "ON_GOING_TRANSACTION"
        ):
            # room_seeker = receive_dict["seeker"].split("+")[-1]
            # room_provider = receive_dict["provider"].split("+")[-1]

            room_seeker = receive_dict["data"]["seeker"]
            room_provider = receive_dict["data"]["provider"]

            receive_dict["data"]["provider_msg"] = await self.get_previous_messages(
                receive_dict["data"]["transaction_id"])
            receive_dict["data"]["user_msg"] = "qwerty"
            if receive_dict["data"]["provider"]:
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
                        'receive_dict': receive_dict,
                    }
                )

    async def send_to_receiver_data(self, event):
        receive_dict = event['receive_dict']
        if type(receive_dict) == str:
            receive_dict = json.loads(receive_dict)

        await self.send(text_data=json.dumps({
            'message': receive_dict,
            "user": str(self.user.id)
        }))

    async def send_pending_data(self, event):
        receive_dict = event['receive_dict']
        if type(receive_dict) == str:
            receive_dict = json.loads(receive_dict)

        await self.send(text_data=json.dumps({
            'message': receive_dict,
            "user": str(self.user.id)
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

    @database_sync_to_async
    def get_direction(self, seeker_location, provider_location):
        user = self.user
        try:
            return ""
        except:
            return ""

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
                    'id', flat=True
                )
            )
            user_list = [str(id) for id in user_provider_list]
            return user_list
        except:
            return

    @database_sync_to_async
    def update_request_instance(self, data):
        try:
            print(data)
            amount = data["data"]["amount"]
            preferred = data["data"]["preferred"]
            # t_req = TransactionRequest.objects.get(seeker__phone_number=seeker)
            # t_req.provider = provider
            # t_req.status="ACCEPTED"
            # t_req.save()
            provider = User.objects.get(id=data["data"]["provider"])
            seeker = User.objects.get(id=data["data"]["seeker"])
            transaction = Transaction.objects.create(
                total_amount=amount,
                preferred_notes=preferred,
                provider=provider,
                seeker=seeker,
                charge=amount * 0.01
            )
            return transaction.id
        except:
            return 0

    @database_sync_to_async
    def get_user_location(self, user):
        try:
            location = "100, 100"
            return location
        except:
            return "0"

    @database_sync_to_async
    def get_previous_messages(self, transaction_id):

        try:
            messages = list(TransactionMessages.objects.filter(transaction_id=transaction_id).values(
                "created_at",
                "user",
                "message"
            ))
            return messages
        except:
            return []

    @database_sync_to_async
    def get_seeker_info(self, seeker):
        try:
            seeker = User.objects.get(id=seeker)
            pic_url = seeker.user_info.profile_pic.url
            return {
                "name": seeker.user_info.person_name,
                "picture": {
                    "url": settings.DOMAIN_NAME + pic_url,
                    "hash": get_hash(pic_url)
                },
                "rating": seeker.userrating_user.rating,
                "total_deals": seeker.userrating_user.no_of_transaction
            }
        except:
            return {
                "name": "",
                "picture": "",
                "rating": 0.0,
                "total_deals": 0
            }

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
        raise InterruptExecution("Stop the task")
