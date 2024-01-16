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
    #
    # channel_layer.group_send(
    #     "dummy", {
    #         'type': 'send.data',
    #         'receive_dict': message,
    #     },
    #     # immediately=True
    # )




@shared_task(bind=True, name='queue_ws_event', ignore_result=True, queue='wsQ')
def queue_ws_event( ws_channel, ws_event:dict, group=True):
    channel_layer = get_channel_layer()
    if group:
        async_to_sync(channel_layer.group_send)(ws_channel,ws_event)
    else:
        async_to_sync(channel_layer.send)(ws_channel,ws_event)