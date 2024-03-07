import asyncio
import json
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.core.cache import cache
from django.conf import settings
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction
from asgiref.sync import async_to_sync, sync_to_async
from datetime import datetime, timedelta
from locations.models import UserLocation
from transactions.models import TransactionRequest, Transaction, TransactionMessages, UserTransactionResponse
from users.models import User
from utils.apps.location import get_directions
from utils.apps.transaction import get_transaction_id
from utils.helper import get_original_hash
from ..tasks import post_timestamp, update_timestamp
from utils.apps.location import get_user_list
from utils.apps.analytics import get_home_analytics_of_user_set
from django.db.models import Q


class VangtiRequestConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.reject_received = False

    async def connect(self):
        self.user = self.scope["user"]
        room_name = self.user.id
        self.room_group_name = f"{room_name}-room"
        # print("all items", self.scope, self.scope["user"], self.scope.get("url_route")["kwargs"], self.channel_layer, self.room_group_name, "\nCONNECTED!!!!!!!!  ", self.scope["user"])
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        msg_data = await self.get_home_analytics(self.user)
        await self.send(text_data=json.dumps({
            'message': msg_data
        }))

        # # send analytics
        # send_own_users_home_analytics(self.user)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # ping-pong for app/frontend
        if text_data == "ping":
            await self.send(text_data=json.dumps({
                'message': "pong",
            }))
            return
        receive_dict = {}
        try:
            if type(text_data) == str:
                receive_dict = json.loads(text_data)
        except:
            return
        print("all data!!!!\n", receive_dict)
        status = receive_dict["status"]
        if "seeker" in receive_dict["data"]:
            if receive_dict["data"]["seeker"] == str(self.user.id) and status == "PENDING":
                user_list = await self.get_user_list(receive_dict)
                print("user list", user_list)
                # cache set for nearby users
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
                await self.send(text_data=json.dumps({
                    'message': receive_dict,
                    'user': str(self.user.id)
                }))
                receive_dict["status"] = status  # setting the initial status

        await self.condition_gate(receive_dict)

    async def condition_gate(self, receive_dict):
        if receive_dict["request"] == "TRANSACTION":
            # send out request
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
                update_timestamp.delay(receive_dict["data"]["seeker"], receive_dict["data"]["provider"])
                # reject message sent to self
                await self.send(text_data=json.dumps({
                    'message': receive_dict,
                    "user": str(self.user.id)
                }))
                await self.receive_reject(receive_dict)

            # accept request
            if (
                    receive_dict["data"]["provider"] == str(self.user.id) and
                    receive_dict["request"] == "TRANSACTION" and
                    receive_dict["status"] == "ACCEPTED"
            ):
                update_timestamp.delay(receive_dict["data"]["seeker"], receive_dict["data"]["provider"])
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
                    receive_dict["status"] == "ON_GOING_TRANSACTION"
            ):
                await self.receive_message_user(receive_dict)

    async def send_to_receiver_data(self, event):
        print("event", event)
        receive_dict = event['receive_dict']

        if type(receive_dict) == str:
            receive_dict = json.loads(receive_dict)
        await self.send(text_data=json.dumps({
            'message': receive_dict,
            "user": str(self.user.id)
        }))

    async def delayed_message_seeker(self, receive_dict):
        provider = receive_dict["data"]["provider"]
        # wait and check cache for 10 seconds
        for i in range(0, 10):
            await asyncio.sleep(1)
            print("cache value ", cache.get(f'{receive_dict["data"]["seeker"]}-request'))
            if cache.get(f'{receive_dict["data"]["seeker"]}-request') is None:
                break
            if cache.get(f'{receive_dict["data"]["seeker"]}') is None:  # if no cache, cancelled event
                receive_dict["request"] = "TRANSACTION"
                receive_dict["status"] = "CANCELLED"
                await self.send(text_data=json.dumps({
                    'message': receive_dict,
                    "user": str(self.user.id)
                }))
                await self.channel_layer.group_send(
                    f"{provider}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )
                return
        receive_dict["data"]["provider"] = provider
        receive_dict["data"]["status"] = 'PENDING'
        if cache.get(f'{receive_dict["data"]["seeker"]}-request') is not None:
            await self.set_timeout(receive_dict)

    async def delayed_message(self, receive_dict):
        for i in range(0, 10):
            await asyncio.sleep(1)
            print("cache value ", cache.get(f'{receive_dict["data"]["seeker"]}-request'))
            if cache.get(f'{receive_dict["data"]["seeker"]}-request') is None:
                break
            if cache.get(f'{receive_dict["data"]["seeker"]}') is None:
                receive_dict["request"] = "TRANSACTION"
                receive_dict["status"] = "CANCELLED"
                await self.send(text_data=json.dumps({
                    'message': receive_dict,
                    "user": str(self.user.id)
                }))
                await self.channel_layer.group_send(
                    f"{receive_dict['data']['provider']}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )
                return
        if cache.get(f'{receive_dict["data"]["seeker"]}-request') is not None:
            await self.set_timeout(receive_dict)

    async def set_timeout(self, receive_dict):
        state = cache.get(
            f'{receive_dict["data"]["seeker"]}-request',
        )
        if state is not None:
            own_provider = receive_dict["data"]["provider"]
            cache_provider = state[0]
            if cache_provider == own_provider:
                receive_dict["status"] = "TIMEOUT"
                await self.channel_layer.group_send(
                    f"{cache_provider}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )
                receive_dict["status"] = "REJECTED"
                await self.receive_reject(receive_dict)

    async def receive_pending(self, receive_dict):
        # cache get
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
        # seeker request time stamp
        if (
                receive_dict["request"] == "TRANSACTION"
                and receive_dict["status"] == "PENDING"

        ):
            if receive_dict["data"]["seeker"] is not None and receive_dict["data"]["provider"] is not None:
                print("here")
                post_timestamp.delay(receive_dict["data"]["seeker"], receive_dict["data"]["provider"])
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
        if len(user_list) != 0:
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
                # seeker request time stamp
                if (
                        receive_dict["request"] == "TRANSACTION"
                        and receive_dict["status"] == "PENDING"

                ):
                    if receive_dict["data"]["seeker"] is not None and receive_dict["data"]["provider"] is not None:
                        print("here")
                        post_timestamp.delay(receive_dict["data"]["seeker"], receive_dict["data"]["provider"])

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
        cache.delete(
            f'{receive_dict["data"]["seeker"]}'
        )
        await self.send_location(receive_dict)

    async def send_location(self, receive_dict):
        transaction_id = receive_dict["data"]["transaction_id"]
        receive_dict = {
            "request": "LOCATION",
            "status": "ON_GOING_TRANSACTION",
            "data": {
                "transaction_id": transaction_id,
                "location": {
                    "latitude": 0.0,
                    "longitude": 0.0
                }
            }
        }
        await self.receive_location(receive_dict)

    async def receive_location(self, receive_dict):
        if (
                "latitude" in receive_dict["data"]["location"]
                and
                "longitude" in receive_dict["data"]["location"]
        ):
            if (
                    receive_dict["data"]["location"]["latitude"] == 0 or
                    receive_dict["data"]["location"]["longitude"] == 0
            ):
                receive_dict["data"]["location"] = await self.get_user_location(self.user.id)
        print(receive_dict["data"]["location"])
        # directions
        # modify data
        receive_dict["data"] = await self.get_direction_data(
            receive_dict["data"]
        )
        if receive_dict["data"] == -1:
            receive_dict["status"] = "INVALID_TRANSACTION"
            receive_dict["data"] = None
            await self.send(text_data=json.dumps({
                'message': receive_dict,
                'user': str(self.user.id)
            }))
            return
        if receive_dict["data"] == -2:
            receive_dict["status"] = "COMPLETED_TRANSACTION"
            receive_dict["data"] = None
            await self.send(text_data=json.dumps({
                'message': receive_dict,
                'user': str(self.user.id)
            }))
            return

        # send location to seeker, provider
        cache.set(
            f"transaction-{receive_dict['data']['transaction_id']}", receive_dict, timeout=None
        )
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

    async def receive_message_user(self, receive_dict):
        if "transaction_id" in receive_dict["data"]:
            transaction_obj_user = await self.get_transaction_obj_party(
                receive_dict["data"]["transaction_id"],
                self.user)
            if transaction_obj_user == -1:
                receive_dict["status"] = "INVALID_TRANSACTION"
                receive_dict["data"] = None
                await self.send(text_data=json.dumps({
                    'message': receive_dict,
                    'user': str(self.user.id)
                }))
                return
            if transaction_obj_user == -2:
                receive_dict["status"] = "COMPLETED_TRANSACTION"
                receive_dict["data"] = None
                await self.send(text_data=json.dumps({
                    'message': receive_dict,
                    'user': str(self.user.id)
                }))
                return
            # transaction_obj
            if "message" in receive_dict["data"]:
                # edit datetime
                receive_dict["data"]["created_at"] = str(datetime.now())
                msg_obj = await self.post_transaction_messages(
                    receive_dict["data"]["transaction_id"],
                    self.user,
                    receive_dict["data"]["message"]
                )
                if msg_obj is None:
                    receive_dict["status"] = "SEND_FAILED"
                    receive_dict["data"] = None
                    await self.send(text_data=json.dumps({
                        'message': receive_dict,
                        'user': str(self.user.id)
                    }))
                    return
            # transaction_obj
            await self.channel_layer.group_send(
                f"{transaction_obj_user}-room",
                {
                    'type': 'send_to_receiver_data',
                    'receive_dict': receive_dict,
                }
            )

    @database_sync_to_async
    def get_user_list(self, room_name):
        user = self.user
        try:
            center = UserLocation.objects.using('location').get(user=user.id).centre
            radius = settings.LOCATION_RADIUS
            user_location_list = list(
                UserLocation.objects.using('location').filter(
                    centre__distance_lte=(center, D(km=radius))
                ).annotate(
                    distance=Distance('centre', center)
                ).order_by(
                    'distance'
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
            on_going_txn = list(Transaction.objects.filter(
                Q(seeker__in=user_provider_list) | Q(provider__in=user_provider_list)
            ).filter(
                is_completed=False
            ).values_list('seeker_id', 'provider_id'))
            on_going_users = [usr for user in on_going_txn for usr in user]

            user_list = [str(id) for id in user_provider_list if id not in on_going_users]

            # user_list = [str(id) for id in user_provider_list ]
            return user_list
        except:
            return

    @database_sync_to_async
    def update_request_instance(self, data):
        try:
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
            location = UserLocation.objects.using("location").filter(user=user_id).last()
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
        # employ cache
        try:
            transaction_obj = Transaction.objects.get(id=transaction_id)
            data["seeker"] = str(transaction_obj.seeker.id)
            data["provider"] = str(transaction_obj.provider.id)

            if transaction_obj.seeker == self.user:
                data["seeker_location"] = data["location"]
                seek = UserLocation.objects.using("location").filter(user=transaction_obj.seeker.id).last()
                seek.latitude = data["location"]["latitude"]
                seek.longitude = data["location"]["longitude"]
                seek.save()
                prov = UserLocation.objects.using("location").filter(user=transaction_obj.provider.id).last()
                data["provider_location"] = {
                    "latitude": prov.latitude,
                    "longitude": prov.longitude
                }
            if transaction_obj.provider == self.user:
                seek = UserLocation.objects.using("location").filter(user=transaction_obj.seeker.id).last()
                data["seeker_location"] = {
                    "latitude": seek.latitude,
                    "longitude": seek.longitude
                }
                data["provider_location"] = data["location"]
                prov = UserLocation.objects.using("location").filter(user=transaction_obj.provider.id).last()
                prov.latitude = data["location"]["latitude"]
                prov.longitude = data["location"]["longitude"]
                prov.save()
            del data["location"]
        except:
            return -1
        if transaction_obj.is_completed:
            return -2

        try:
            # get_directions(seeker_location, provider_location)
            data["direction"] = get_directions(transaction_id, data["seeker_location"], data["provider_location"])
        except:
            return -1
        return data

    @database_sync_to_async
    def get_transaction_obj_party(self, transaction_id, user):
        transaction_id = get_transaction_id(transaction_id)
        try:
            transaction_obj = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return -1
        if transaction_obj.is_completed:
            return -2
        if user == transaction_obj.seeker:
            return str(transaction_obj.provider.id)

        if user == transaction_obj.provider:
            return str(transaction_obj.seeker.id)

    @database_sync_to_async
    def get_transaction_instance(self, transaction_id, user):
        transaction_id = get_transaction_id(transaction_id)
        try:
            transaction_obj = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return -1
        if transaction_obj.is_completed:
            return -2
        if user != transaction_obj.seeker:
            return -3

        return {
            "seeker": str(transaction_obj.seeker.id),
            "provider": str(transaction_obj.provider.id)
        }

    @database_sync_to_async
    def post_transaction_messages(self, transaction_id, user, message):
        try:
            transaction_id_no = get_transaction_id(transaction_id)
            messages = TransactionMessages.objects.create(
                transaction_id=transaction_id_no,
                user=user,
                message=message
            )
            return messages
        except:
            return None

    @database_sync_to_async
    def get_seeker_info(self, seeker):
        print("seeker", seeker, self.user.id)
        try:
            seeker = User.objects.get(id=self.user.id)
            try:
                pic_url = settings.DOMAIN_NAME + str(seeker.user_info.profile_pic.url)
            except:
                pic_url = None

            try:
                url_hash = get_original_hash(seeker.user_info.profile_pic.url)
            except:
                url_hash = None

            return {
                "name": seeker.user_info.person_name,
                "picture": {
                    "url": pic_url,
                    "hash": url_hash
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

    @database_sync_to_async
    def get_home_analytics(self, user):
        user_set = get_user_list(user)
        rate_data = get_home_analytics_of_user_set(user_set)
        message = {
            "request": "ANALYTICS",
            "status": "ACTIVE",
            'data': rate_data
        }
        return message
