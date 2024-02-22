from core.celery import app
from .models import *
from datetime import datetime
from celery import shared_task
# from utils.apps.web_socket import send_message_to_channel
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_message_to_channel(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"{user_id}-room",
        {
            "type": "send_to_receiver_data",
            'receive_dict': message
        }
    )
    return


@shared_task
def send_out_mesg(some_list):
    print(some_list)
    # print(request.user)
    for ins in some_list:
        user = ins.pop("user")
        message = {
            "request": "ANALYTICS",
            "status": "ACTIVE",
            'data': ins
        }
        # for i in range(3):
        send_message_to_channel(str(user), message)
    return

# @shared_task
# def send_out_mesg():
#     for i in range(100000):
#         print("in celery")
#
#     return
