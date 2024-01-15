import time
from time import sleep
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.celery import app
from channels.layers import get_channel_layer
# from celery.decorators import task


@shared_task()
def send_auto_reject():
    # sleep(3)
    message = {
        "seeker": "+8801234567891",
        "amount": 900,
        "preferred": "100,20",
        "request": "ol",
        "provider": ""
    }
    # async_to_sync(channel_layer.group_send)(
    #     "8801234567891-room", {
    #             'type': 'send.data',
    #             'receive_dict': message,
    #     }, immediately=True
    # )
    channel_layer = get_channel_layer()
    channel_layer.group_send(
        "8801234567891-room", {
            'type': 'send.data',
            'receive_dict': message,
        },
        # immediately=True
    )

    # Group("test").send({
    #     "text": json.dumps({
    #         'type': 'test',
    #     })
    # }, immediately=True)
