import asyncio
import json
from django.core.cache import cache
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from django.db import transaction
from asgiref.sync import async_to_sync, sync_to_async
from datetime import datetime, timedelta
from itertools import cycle
from transactions.models import (
    Transaction, TransactionMessages, UserTransactionResponse, UserAppActivityMode, UserOnTxnRequest
)
from users.models import User
from utils.apps.transaction import get_transaction_id
from utils.apps.analytics import get_home_analytics_of_user_set
from utils.apps.web_socket_helper import (
    get_user_information, get_transaction_instance,
    create_transaction_instance, get_providers, iterate_over_cycle
)
from utils.apps.location import get_user_list, update_user_location_instance, get_user_location_instance, get_directions
from utils.log import logger
from ..tasks import (
    update_providers_timestamps, send_push_notif,
    create_on_req_user, delete_on_req_user
)


class VangtiRequestConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        self.user = self.scope["user"]
        room_name = self.user.id
        self.room_group_name = f"{room_name}-room"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # # send analytics
        msg_data = await self.get_home_analytics(self.user)
        await self.send(text_data=json.dumps({
            'message': msg_data
        }))

        # change user active state
        await self.user_activity_connect(self.user)

    async def disconnect(self, close_code):
        # change user active state
        await self.user_activity_disconnect(self.user)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        raise StopConsumer()

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

        # logger.info("all data!!!!\n %s", f"{receive_dict}")
        status = receive_dict["status"]
        if "seeker" in receive_dict["data"]:
            if receive_dict["data"]["seeker"] == str(self.user.id) and status == "PENDING":
                user_list = await self.fetch_user_list(receive_dict)
                logger.info("user list %s", f"{user_list}")

                # cache set for nearby users
                if len(user_list) == 0:
                    receive_dict.update({"status": "NO_PROVIDER"})
                    # receive_dict["status"] = "NO_PROVIDER"
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
                    timeout=900
                )
                # receive_dict["status"] = "SEARCHING"
                receive_dict.update({"status": "SEARCHING"})
                await self.send(text_data=json.dumps({
                    'message': receive_dict,
                    'user': str(self.user.id)
                }))
                receive_dict.update({"status": status})  # setting the initial status

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
                # sent to self
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
                await self.receive_accept(receive_dict)

        # location
        if (
                receive_dict["request"] == "LOCATION" and
                receive_dict["status"] == "ON_GOING_TRANSACTION"
        ):
            await self.receive_location(receive_dict)

        # message
        if receive_dict["request"] == "MESSAGE":
            if receive_dict["status"] == "ON_GOING_TRANSACTION":
                await self.receive_message_user(receive_dict)

    async def send_to_receiver_data(self, event):
        logger.info("event %s", f"{event}")
        receive_dict = event['receive_dict']
        if type(receive_dict) == str:
            receive_dict = json.loads(receive_dict)
        await self.send(text_data=json.dumps({'message': receive_dict, "user": str(self.user.id)}))

    async def delayed_message(self, receive_dict):
        for i in range(0, 30):  # time 30 sec/provider
            await asyncio.sleep(1)
            logger.info("cache log %s", f"{i}")
            if cache.get(f'{receive_dict["data"]["seeker"]}-request') is None:
                break
            if (cancelled_request := cache.get(f'{receive_dict["data"]["seeker"]}')) is None:
                receive_dict.update({"status": "CANCELLED"})
                await self.send(text_data=json.dumps({
                    'message': receive_dict, "user": str(self.user.id)
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
        own_provider = receive_dict["data"]["provider"]
        cache_provider = cache.get(
            f'{receive_dict["data"]["seeker"]}-request',
        )
        if cache_provider is not None:
            if cache_provider == own_provider:
                receive_dict["status"] = "TIMEOUT"
                await self.channel_layer.group_send(
                    f"{cache_provider}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )
                receive_dict.update({"status": "REJECTED"})
                # receive_dict["status"] = "REJECTED"
                await self.receive_reject(receive_dict)

    async def receive_pending(self, receive_dict):
        # cache get
        user_list = cache.get(receive_dict["data"]["seeker"])
        print("before iterating user_list", user_list)
        user_list = await self.lookup_user_list(receive_dict["data"]["seeker"], user_list)
        print("after iterating user_list", user_list)
        # cache set for timestamps for providers
        cache.set(
            f'{receive_dict["data"]["seeker"]}-timestamp',
            [[user_list[0], datetime.now()]],
            timeout=300
        )
        # create on req user
        create_on_req_user.delay(user_list[0])

        # user list
        receive_dict["data"]["provider"] = user_list[0]

        # get seeker info
        receive_dict["data"]["seeker_info"] = await self.get_seeker_info(
            receive_dict["data"]["seeker"]
        )

        # cache set for counting timeout
        cache.set(
            f'{receive_dict["data"]["seeker"]}-request',
            receive_dict["data"]["provider"],
            timeout=300
        )

        await self.channel_layer.group_send(
            f"{receive_dict['data']['provider']}-room",
            {
                'type': 'send_to_receiver_data',
                'receive_dict': receive_dict,
            }
        )

        # send push notification to provider
        send_push_notif.delay(receive_dict['data']['provider'], receive_dict)

        # send for timeout counting
        await self.delayed_message(receive_dict)

    async def receive_reject(self, receive_dict):
        user_list = cache.get(receive_dict["data"]["seeker"])


        user_list_length = len(user_list)

        if user_list_length != 0:
            if user_list[0] == receive_dict["data"]["provider"]:
                user_list.pop(0)
                delete_on_req_user.delay(receive_dict["data"]["provider"])

                print("before iterating user_list", user_list)
                user_list = await self.lookup_user_list(receive_dict["data"]["seeker"], user_list)
                print("after iterating user_list", user_list)
                # delete req user

                # after popping user
                user_list_length = len(user_list)
                cache.set(receive_dict["data"]["seeker"], user_list)

                # timestamp'
                timestamp_list = cache.get(
                    f'{receive_dict["data"]["seeker"]}-timestamp'
                )
                timestamp_list[-1].append(datetime.now())

                # delete user req
                delete_on_req_user.delay(timestamp_list[-1][0])
                
                # print(timestamp_list)
                # print("hi there")
                if user_list_length != 0:
                    timestamp_list.append([user_list[0], datetime.now()])
                    # create user req
                    create_on_req_user.delay(user_list[0])

                cache.set(f'{receive_dict["data"]["seeker"]}-timestamp', timestamp_list, timeout=300)

                # logger.info("in reject timestamp list %s", f"{timestamp_list}")

        if user_list_length != 0:
            receive_dict["data"]["provider"] = user_list[0]
            receive_dict.update({"status": "PENDING"})
            # receive_dict["status"] = "PENDING"
            if cache.get(f'{receive_dict["data"]["seeker"]}-request') is not None:
                cache.set(
                    f'{receive_dict["data"]["seeker"]}-request',
                    receive_dict["data"]["provider"],
                    timeout=60
                )
                await self.channel_layer.group_send(
                    f"{user_list[0]}-room",
                    {
                        'type': 'send_to_receiver_data',
                        'receive_dict': receive_dict,
                    }
                )
                await self.delayed_message(receive_dict)
        else:
            # no provider section
            update_providers_timestamps.delay(
                receive_dict["data"]["seeker"],
                cache.get(f'{receive_dict["data"]["seeker"]}-timestamp'))

            receive_dict.update({"status": "NO_PROVIDER"})
            # receive_dict["status"] = "NO_PROVIDER"
            cache.delete(f'{receive_dict["data"]["seeker"]}-request')
            await self.channel_layer.group_send(
                f'{receive_dict["data"]["seeker"]}-room',
                {
                    'type': 'send_to_receiver_data',
                    'receive_dict': receive_dict,
                }
            )

    async def receive_accept(self, receive_dict):
        receive_dict.update({"status": "ON_GOING_TRANSACTION"})
        # receive_dict["status"] = "ON_GOING_TRANSACTION"
        receive_dict["data"]["transaction_id"] = await self.create_new_transaction(receive_dict["data"])
        if receive_dict["data"]["provider"]:
            await self.channel_layer.group_send(
                f'{receive_dict["data"]["seeker"]}-room',
                {
                    'type': 'send_to_receiver_data',
                    'receive_dict': receive_dict,
                }
            )
            await self.channel_layer.group_send(
                f'{receive_dict["data"]["provider"]}-room', {
                    'type': 'send_to_receiver_data',
                    'receive_dict': receive_dict,
                }
            )

        # timestamp'
        timestamp_list = cache.get(f'{receive_dict["data"]["seeker"]}-timestamp')
        timestamp_list[-1].append(datetime.now())
        # delete user req
        delete_on_req_user.delay(timestamp_list[-1][0])

        cache.set(f'{receive_dict["data"]["seeker"]}-timestamp', timestamp_list, timeout=300)
        # logger.info("in accept timestamp list %s", f"{timestamp_list}")

        update_providers_timestamps.delay(
            receive_dict["data"]["seeker"],
            # cache.get(f'{receive_dict["data"]["seeker"]}-timestamp')
            timestamp_list
        )

        # send push notification to seeker
        send_push_notif.delay(receive_dict['data']['seeker'], receive_dict)

        cache.delete(
            f'{receive_dict["data"]["seeker"]}-request'
        )
        cache.delete(
            f'{receive_dict["data"]["seeker"]}'
        )
        cache.delete(
            f'{receive_dict["data"]["seeker"]}-timestamp'
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
                if receive_dict["data"]["location"] is None:
                    return

        # directions
        receive_dict["data"] = await self.get_direction_data(receive_dict["data"])
        if receive_dict["data"] in [-1, -2]:
            if receive_dict["data"] == -1:
                receive_dict.update({"status": "INVALID_TRANSACTION"})
            if receive_dict["data"] == -2:
                receive_dict.update({"status": "COMPLETED_TRANSACTION"})
            receive_dict.update({"data": None})
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

    async def receive_message_user(self, receive_dict):
        if "transaction_id" not in receive_dict["data"]:
            return
        transaction_obj_user = await self.get_transaction_party(
            receive_dict["data"]["transaction_id"],
            self.user)
        if transaction_obj_user in [-1, -2]:
            if transaction_obj_user == -1:
                receive_dict.update({"status": "INVALID_TRANSACTION"})
                # receive_dict["status"] = "INVALID_TRANSACTION"
            elif transaction_obj_user == -2:
                receive_dict.update({"status": "COMPLETED_TRANSACTION"})
                # receive_dict["status"] = "COMPLETED_TRANSACTION"
            receive_dict.update({"data": None})
            await self.send(text_data=json.dumps({
                'message': receive_dict,
                'user': str(self.user.id)
            }))
            return

        # transaction_obj
        if "message" in receive_dict["data"]:
            # edit datetime
            msg_obj = await self.post_transaction_messages(
                receive_dict["data"]["transaction_id"],
                self.user,
                receive_dict["data"]["message"]
            )
            if msg_obj is None:
                receive_dict.update({"status": "SEND_FAILED", "data": None})
                # receive_dict["status"] = "SEND_FAILED"
                # receive_dict["data"] = None
                await self.send(text_data=json.dumps({
                    'message': receive_dict,
                    'user': str(self.user.id)
                }))
                return
            receive_dict["data"]["created_at"] = str(msg_obj.created_at.astimezone())

            await self.channel_layer.group_send(
                f"{transaction_obj_user}-room",
                {
                    'type': 'send_to_receiver_data',
                    'receive_dict': receive_dict,
                }
            )

            # send push notification to user
            send_push_notif.delay(transaction_obj_user, receive_dict)

    @database_sync_to_async
    def fetch_user_list(self, room_name):
        user = self.user
        # try:
        #     return get_providers(user)
        # except:
        #     return []
        return get_providers(user)

    @database_sync_to_async
    def create_new_transaction(self, data):
        try:
            return create_transaction_instance(data)
        except:
            return str(0)

    @database_sync_to_async
    def get_user_location(self, user_id):
        try:
            location = get_user_location_instance(user_id)
            return {
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        except:
            return None

    @database_sync_to_async
    def get_direction_data(self, data):
        try:
            transaction_obj = get_transaction_instance(data["transaction_id"])
            data["seeker"] = str(transaction_obj.seeker.id)
            data["provider"] = str(transaction_obj.provider.id)

            if transaction_obj.seeker == self.user:
                seek = update_user_location_instance(transaction_obj.seeker.id, data["location"])
                prov = get_user_location_instance(transaction_obj.provider.id)
                data["seeker_location"] = data["location"]
                data["provider_location"] = {"latitude": prov.latitude, "longitude": prov.longitude}

            if transaction_obj.provider == self.user:
                seek = get_user_location_instance(transaction_obj.seeker.id)
                prov = update_user_location_instance(transaction_obj.provider.id, data["location"])
                data["seeker_location"] = {"latitude": seek.latitude, "longitude": seek.longitude}
                data["provider_location"] = data["location"]

            del data["location"]

        except:
            return -1
        if transaction_obj.is_completed:
            return -2
        try:
            data["direction"] = get_directions(transaction_obj.id, data["seeker_location"], data["provider_location"])
        except:
            data["direction"] = {
                "distance": f"{0} meter",
                "duration": f"{0} sec",
                "polyline": None
            }
        return data

    @database_sync_to_async
    def get_transaction_party(self, transaction_id, user):
        transaction_obj = get_transaction_instance(transaction_id)
        if transaction_obj == -1:
            return -1
        if transaction_obj.is_completed:
            return -2
        if user == transaction_obj.seeker:
            return str(transaction_obj.provider.id)
        if user == transaction_obj.provider:
            return str(transaction_obj.seeker.id)

    @database_sync_to_async
    def post_transaction_messages(self, transaction_id, user, message):
        try:
            return TransactionMessages.objects.create(
                transaction_id=get_transaction_id(transaction_id),
                user=user,
                message=message
            )
        except:
            return None

    @database_sync_to_async
    def get_seeker_info(self, seeker):
        try:
            return get_user_information(User.objects.get(id=seeker))
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
        # excluding the requesting user
        # user_set = user_set.exclude(id=user.id)
        message = {
            "request": "ANALYTICS",
            "status": "ACTIVE",
            'data': get_home_analytics_of_user_set(user_set)
        }
        return message

    @database_sync_to_async
    def user_activity_connect(self, user):
        if getattr(user, "user_app_mode", None) is not None:
            user.user_app_mode.is_active = True
            user.user_app_mode.save()
            return
        UserAppActivityMode.objects.create(
            user=user,
            is_active=True
        )
        return

    @database_sync_to_async
    def user_activity_disconnect(self, user):
        if getattr(user, "user_app_mode", None) is not None:
            user.user_app_mode.is_active = False
            user.user_app_mode.save()
            return
        UserAppActivityMode.objects.create(
            user=user,
            is_active=False
        )
        return

    @database_sync_to_async
    def lookup_user_list(self, seeker, user_list):
        # print("here in look up.........")
        new_list = iterate_over_cycle(user_list)

        # if not new_list:
        #     new_prov_list = get_providers(seeker)
        #     final_list = iterate_over_cycle(new_prov_list)
        #     if final_list:
        #         return final_list
        return new_list


        # for user in user_list:
        #     provider_on_req = UserOnTxnRequest.objects.filter(user_id=user)
        #     print("found! on provider request", provider_on_req)
        #     if provider_on_req.exists():
        #         continue
            # user
        # for user in user_list:
        #     try:
        #         print(user, "looking up")
        #         provider_on_req = UserOnTxnRequest.objects.get(user_id__str=user)
        #         print("found! on provider request", provider_on_req)
        #         # if provider_on_req:
        #         #     return
        #     except UserOnTxnRequest.DoesNotExist:
        #         print(user, "looking up")
        #         provider_on_req = UserOnTxnRequest.objects.get(user_id__str=user)
        #         print("found! on provider request", provider_on_req)
        #         # if provider_on_req:
        #         #     return
        #
        #         # return provider
        #         print("in exception")

