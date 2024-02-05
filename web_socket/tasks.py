import time

from django.conf import settings
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from core.celery import app
# from celery.decorators import task
from django.contrib.auth import authenticate, login
import requests


@shared_task()
def send_celery(query_string):
    print("helo dummy")
    token = query_string.decode("utf-8").split("=")[-1]



@app.task
def test_task(arg):
    print("helo task", arg)
