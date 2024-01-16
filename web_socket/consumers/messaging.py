import json
from channels.db import database_sync_to_async
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from locations.models import UserLocation, LocationRadius
from ..fcm import send_push
from transactions.models import Transaction
from ..models import *

"""transaction_id-message-room"""

"""
{
"transaction":"phone",
"user":"",
"message": 51,
}
{
"request":"get",
"data":{}
}
{
"request":"post",
"data":{
"transaction":1,
"user":"",
"message": "helo friend"
}
}
"""


class TransactionMessageConsumer(AsyncWebsocketConsumer):
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
        transaction = await self.get_transaction(self.room_group_name)
        if transaction is None:
            return

        if receive_dict["request"] == "get":
            user = self.user
            data = receive_dict["data"]
            get_msg = await self.get_transaction_msg(transaction)
            receive_dict = {
                "request": "response",
                "transaction": transaction,
                "data": get_msg
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send.sdpt',
                    'receive_dict': receive_dict,
                }
            )

        if receive_dict["request"] == "post":
            user = self.user
            data = receive_dict["data"]
            create_msg = await self.create_transaction_msg(user, data)

            receive_dict = {
                "request": "response",
                "transaction": data["transaction"],
                "user": self.user.phone_number,
                "message": data["message"]
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send.sdpt',
                    'receive_dict': receive_dict,
                }
            )

        # receive_dict["user"] =self.scope["user"].phone_number
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
            if transaction is None:
                return None
            return transaction.id
        except:
            return None

    @database_sync_to_async
    def create_transaction_msg(self, user, data):
        try:

            return TransactionMessages.objects.create(user=user, transaction_id=data["transaction"],
                                                      message=data["message"])
        except:
            return None

    @database_sync_to_async
    def get_transaction_msg(self, transaction_id):
        try:
            return list(TransactionMessages.objects.filter(transaction_id=transaction_id).values("user__phone_number",
                                                                                                 "message"))
        except:
            return None
