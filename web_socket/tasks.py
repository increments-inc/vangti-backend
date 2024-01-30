from django.conf import settings
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from core.celery import app
# from celery.decorators import task
from django.contrib.auth import authenticate, login
import requests


@shared_task()
def send_celery(scope):
    print("helo dummy")
    # message = {
    #     "seeker": "ajk",
    # }
    # # async_to_sync(channel_layer.group_send)(
    # #     "8801234567891-room", {
    # #             'type': 'send.data',
    # #             'receive_dict': message,
    # #     }, immediately=True
    # # )
    # user = sync_to_async(authenticate)(username="admin", password="admin")
    # print(user)
    # channel_layer = get_channel_layer()
    # channel_layer.group_send(
    #     "dummy", {
    #         'type': 'send.data',
    #         'receive_dict': message,
    #     },
    #     # immediately=True
    # )


@app.task
def test_task(arg):
    print("helo task", arg)
