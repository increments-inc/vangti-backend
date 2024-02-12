import asyncio
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
from utils.apps.location import get_directions
from utils.apps.transaction import get_transaction_id


def get_hash(picture_url):
    with open(picture_url[1:], 'rb') as image_file:
        hash = blurhash.encode(image_file, x_components=4, y_components=3)
    return hash


class VangtiRequestConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reject_received = False

    async def connect(self):
        kwargs = self.scope.get("url_route")["kwargs"]
        self.user = self.scope["user"]
        room_name = self.user.id
        self.room_group_name = f"{room_name}-room"
        print("all items", self.scope, self.scope["user"], kwargs, self.channel_layer, self.room_group_name)
        print("CONNECTED!!!!!!!!  ", self.scope["user"])
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
        user = self.scope["user"]
        receive_dict = text_data
        try:
            if type(text_data) == str:
                receive_dict = json.loads(text_data)
        except:
            print("in exception")
            return
        print("all data!!!!\n", receive_dict)
        status = receive_dict["status"]
        if "seeker" in receive_dict["data"]:
            if receive_dict["data"]["seeker"] == str(self.user.id) and status == "PENDING":
                user_list = await self.get_user_list(receive_dict)
                print("here", user_list)
                # cache set
                if len(user_list) == 0:
                    receive_dict["status"] = "NO_PROVIDER"
                    await self.channel_layer.group_send(
                        f'{receive_dict["data"]["seeker"]}-room',
                        {
                            'type': 'send_to_receiver_data',
                            'receive_dict': receive_dict,
                        }
                    )
                    return
                cache.set(
                    receive_dict["data"]["seeker"],
                    user_list,
                    timeout=None
                )
                receive_dict["status"] = "SEARCHING"
                # await self.channel_layer.group_send(
                #     f'{receive_dict["data"]["seeker"]}-room',
                #     {
                #         'type': 'send_to_receiver_data',
                #         'receive_dict': receive_dict,
                #     }
                # )
                await self.send(text_data=json.dumps({
                    'message': receive_dict,
                    'user': str(self.user.id)
                }))

                receive_dict["status"] = status

        await self.condition_gate(receive_dict)

    async def condition_gate(self, receive_dict):
        # send out request
        if receive_dict["request"] == "TRANSACTION":
            if (
                    receive_dict["data"]["seeker"] == str(self.user.id) and
                    receive_dict["request"] == "TRANSACTION" and
                    receive_dict["status"] == "PENDING" and
                    receive_dict["data"]["provider"] is None
            ):
                await self.receive_pending(receive_dict)

            # reject request
            if (
                    receive_dict["data"]["provider"] == str(self.user.id) and
                    receive_dict["request"] == "TRANSACTION" and
                    receive_dict["status"] == "REJECTED"
            ):
                await self.receive_reject(receive_dict)

            # accept request
            if (
                    receive_dict["data"]["provider"] == str(self.user.id) and
                    receive_dict["request"] == "TRANSACTION" and
                    receive_dict["status"] == "ACCEPTED"
            ):
                await self.receive_accept(receive_dict)

        # location
        if (
                # (receive_dict["data"]["seeker"] == str(self.user.id)
                #  or receive_dict["data"]["provider"] == str(self.user.id))
                # and
                receive_dict["request"] == "LOCATION" and
                receive_dict["status"] == "ON_GOING_TRANSACTION"
        ):
            await self.receive_location(receive_dict)
            # message
        if receive_dict["request"] == "MESSAGE":
            if (
                    (receive_dict["data"]["seeker"] == str(self.user.id)
                     or receive_dict["data"]["provider"] == str(self.user.id))
                    and
                    receive_dict["request"] == "MESSAGE" and
                    receive_dict["status"] == "ON_GOING_TRANSACTION"
            ):
                await self.receive_message(receive_dict)

    async def send_to_receiver_data(self, event):
        print("all send sata !!!!\n", event)
        receive_dict = event['receive_dict']
        if type(receive_dict) == str:
            receive_dict = json.loads(receive_dict)
        await self.send(text_data=json.dumps({
            'message': receive_dict,
            "user": str(self.user.id)
        }))

    async def delayed_message_seeker(self, receive_dict):
        provider = receive_dict["data"]["provider"]

        for i in range(0, 10):
            print("time", i)
            await asyncio.sleep(1)
            print("cache value ", cache.get(f'{receive_dict["data"]["seeker"]}-request'))
            if cache.get(f'{receive_dict["data"]["seeker"]}-request') is None:
                break
        receive_dict["data"]["provider"] = provider
        receive_dict["data"]["status"] = 'PENDING'

        if cache.get(f'{receive_dict["data"]["seeker"]}-request') is not None:
            print("here")
            await self.set_timeout(receive_dict)
        print("10 seconds have passed")

    async def delayed_message(self, receive_dict):
        for i in range(0, 10):
            print("time", i)
            await asyncio.sleep(1)
            print("cache value ", cache.get(f'{receive_dict["data"]["seeker"]}-request'))
            if cache.get(f'{receive_dict["data"]["seeker"]}-request') is None:
                break

        if cache.get(f'{receive_dict["data"]["seeker"]}-request') is not None:
            print("here")
            await self.set_timeout(receive_dict)
        print("10 seconds have passed")

    async def set_timeout(self, receive_dict):
        print("in set timeout")
        state = cache.get(
            f'{receive_dict["data"]["seeker"]}-request',
        )
        if state is not None:
            own_provider = receive_dict["data"]["provider"]
            cache_provider = state[0]
            print("provider ", own_provider, cache_provider)
            if cache_provider == own_provider:
                receive_dict["status"] = "TIMEOUT"
                await self.channel_layer.group_send(
                    f"{cache_provider}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )
                # if cache.get(
                #         f'{receive_dict["data"]["seeker"]}-request',
                # ) is not None:
                #     print("here in 2nd portion\n")
                receive_dict["status"] = "REJECTED"
                await self.receive_reject(receive_dict)

    async def receive_pending(self, receive_dict):
        # receive_dict["status"] = "SEARCHING"
        # # receive_dict["data"]["provider"] = None
        # await self.channel_layer.group_send(
        #     f'{receive_dict["data"]["seeker"]}-room',
        #     {
        #         'type': 'send_to_receiver_data',
        #         'receive_dict': receive_dict,
        #     }
        # )

        # user_list = await self.get_user_list(receive_dict)
        # print("here", user_list)
        # if len(user_list)==0:
        #     receive_dict["status"] = "NO_PROVIDER"
        #     await self.channel_layer.group_send(
        #         f'{receive_dict["data"]["seeker"]}-room',
        #         {
        #             'type': 'send_to_receiver_data',
        #             'receive_dict': receive_dict,
        #         }
        #     )
        #     return
        # cache set
        user_list = cache.get(
            receive_dict["data"]["seeker"]
        )

        send_user = user_list[0]
        receive_dict["data"]["provider"] = user_list[0]
        receive_dict["data"]["seeker_info"] = await self.get_seeker_info(
            receive_dict["data"]["seeker"]
        )
        cache.set(
            f'{receive_dict["data"]["seeker"]}-request',
            [
                receive_dict["data"]["provider"], "pending"
            ],
            timeout=None
        )
        receive_dict["status"] = "PENDING"
        await self.channel_layer.group_send(
            f"{send_user}-room",
            {
                'type': 'send_to_receiver_data',
                'receive_dict': receive_dict,
            }
        )
        receive_dict["data"]["provider"] = send_user
        await self.delayed_message_seeker(receive_dict)

    async def receive_reject(self, receive_dict):
        user_list = cache.get(receive_dict["data"]["seeker"])
        print(user_list)
        if user_list[0] == receive_dict["data"]["provider"]:
            user_list.pop(0)
            cache.set(receive_dict["data"]["seeker"], user_list)
        if len(user_list) != 0:
            send_user = user_list[0]
            receive_dict["data"]["provider"] = user_list[0]
            receive_dict["status"] = "PENDING"
            if cache.get(f'{receive_dict["data"]["seeker"]}-request') is not None:
                cache.set(
                    f'{receive_dict["data"]["seeker"]}-request',
                    [
                        receive_dict["data"]["provider"], "pending"
                    ],
                    timeout=60
                )
                await self.channel_layer.group_send(
                    f"{send_user}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )
                await self.delayed_message(receive_dict)
        else:
            room_seeker = receive_dict["data"]["seeker"]
            receive_dict["status"] = "NO_PROVIDER"
            cache.delete(
                f'{receive_dict["data"]["seeker"]}-request'
            )
            await self.channel_layer.group_send(
                f"{room_seeker}-room",
                {
                    'type': 'send_to_receiver_data',
                    'receive_dict': receive_dict,
                }
            )

    async def receive_accept(self, receive_dict):
        room_seeker = receive_dict["data"]["seeker"]
        room_provider = receive_dict["data"]["provider"]
        transaction_id = await self.update_request_instance(receive_dict)
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
        cache.delete(
            f'{receive_dict["data"]["seeker"]}-request'
        )

    async def receive_location(self, receive_dict):
        user = self.user.id
        print("location", user)
        if (
                "latitude" in receive_dict["data"]["location"]
                and
                "longitude" in receive_dict["data"]["location"]
        ):
            if (
                    receive_dict["data"]["location"]["latitude"] == 0 or
                    receive_dict["data"]["location"]["longitude"] == 0
            ):
                receive_dict["data"]["location"] = await self.get_user_location(
                    receive_dict["data"]["provider"])

        print(receive_dict["data"]["location"])


        # directions
        # modify data
        receive_dict["data"] = await self.get_direction_data(
            receive_dict["data"]
        )
        if receive_dict["data"] == -1:
            receive_dict["status"] = "INVALID_TRANSACTION"
            receive_dict["data"] = {}
            await self.send(text_data=json.dumps({
                'message': receive_dict,
                'user': str(self.user.id)
            }))
            return

        # send location to seeker, provider
        await self.channel_layer.group_send(
            f"{receive_dict['data']['seeker']}-room",
            {
                'type': 'send_to_receiver_data',
                'receive_dict': receive_dict,
            }
        )
        await self.channel_layer.group_send(
            f"{receive_dict['data']['provider']}-room",
            {
                'type': 'send_to_receiver_data',
                'receive_dict': receive_dict,
            }
        )


    async def receive_message(self, receive_dict):
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

    @database_sync_to_async
    def get_user_list(self, room_name):
        user = self.user
        try:
            print("here")
            center = UserLocation.objects.using('location').get(user=user.id).centre
            radius = settings.LOCATION_RADIUS
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
            provider = User.objects.get(id=data["data"]["provider"])
            seeker = User.objects.get(id=data["data"]["seeker"])
            try:
                transaction = Transaction.objects.get(
                    provider=provider,
                    seeker=seeker,
                    is_completed=False
                )
                transaction.total_amount = amount
                transaction.preferred_notes = preferred,
                transaction.charge = amount * 0.01
                transaction.save()
            except Transaction.DoesNotExist:
                transaction = Transaction.objects.create(
                    total_amount=amount,
                    preferred_notes=preferred,
                    provider=provider,
                    seeker=seeker,
                    charge=amount * 0.01
                )
            transact = transaction.get_transaction_unique_no
            return str(transact)
        except:
            return str(0)

    @database_sync_to_async
    def get_user_location(self, user_id):
        try:
            print("im in here", user_id)
            location = UserLocation.objects.using("location").filter(user=user_id).last()
            print(location)
            return {
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        except:
            return {
                "latitude": 0.0,
                "longitude": 0.0
            }

    @database_sync_to_async
    def get_direction_data(self, data):
        transaction_id = get_transaction_id(data["transaction_id"])
        print("tr", transaction_id)
        # employ cache
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            data["seeker"] =str( transaction.seeker.id)
            data["provider"] = str(transaction.provider.id)
            if transaction.seeker==self.user:
                data["seeker_location"]=data["location"]
                prov = UserLocation.objects.using("location").filter(user=transaction.provider.id).last()
                data["provider_location"] = {
                    "latitude": prov.latitude,
                    "longitude": prov.longitude
                }
            if transaction.provider==self.user:
                seek = UserLocation.objects.using("location").filter(user=transaction.seeker.id).last()
                data["seeker_location"]={
                    "latitude": seek.latitude,
                    "longitude": seek.longitude
                }
                data["provider_location"]=data["location"]
            del data["location"]
        except:
            return -1
        try:
            # get_directions(seeker_location, provider_location)
            data["direction"]= get_directions(transaction_id, data["seeker_location"], data["provider_location"])

        except:
            return -1
        return data

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
                "picture": {
                    "url": "",
                    "hash": ""
                },
                "rating": 0.0,
                "total_deals": 0
            }
