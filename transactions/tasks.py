from core.celery import app
from .models import *
from datetime import datetime
from celery import shared_task
# from utils.apps.web_socket import send_message_to_channel
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from utils.apps.location import get_user_location, get_directions


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
def send_out_analytics_mesg(some_list):
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


@shared_task
def send_out_location_data(user, instance_id):
    instance = Transaction.objects.get(id=instance_id)
    seeker_location = get_user_location(instance.seeker.id)
    provider_location = get_user_location(instance.seeker.id)
    seeker_dict = {
        "latitude": seeker_location[1],
        "longitude": seeker_location[0]
    }
    provider_dict = {
        "latitude": provider_location[1],
        "longitude": provider_location[0]
    }
    direction = get_directions(instance_id, seeker_dict, provider_dict)
    message = {
        'request': 'LOCATION',
        'status': 'ON_GOING_TRANSACTION',
        'data': {
            'transaction_id': instance.get_transaction_unique_no,
            "seeker": f'{instance.seeker.id}',
            "provider": f'{instance.provider.id}',
            "seeker_location": {
                "latitude": seeker_location[1],
                "longitude": seeker_location[0]
            },
            "provider_location": {
                "latitude": provider_location[1],
                "longitude": provider_location[0]
            },
            "direction": direction
        }
    }
    # for i in range(3):
    send_message_to_channel(str(instance.seeker.id), message)
    send_message_to_channel(str(instance.provider.id), message)
    print("in transaction")
    return
