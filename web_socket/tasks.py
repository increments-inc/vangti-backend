import time
import websockets
from django.conf import settings
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from core.celery import app
# from celery.decorators import task
from django.contrib.auth import authenticate, login
import requests
import asyncio
import json

async def send_message(path, token, data):
    async with websockets.connect(
            "ws://127.0.0.1:8000"+path+"?token="+token
    ) as websocket:
        await websocket.send(json.dumps(data))

@app.task
async def send_celery(path, query_string, data):
    for i in range(0, 10):
        print("time", i)
        await asyncio.sleep(1)
    print("helo dummy")
    token = query_string.decode("utf-8").split("=")[-1]
    # asyncio.get_event_loop().run_forever(webs())
    await send_message(path, token, data)

    # print(gh)

@app.task
def test_task(arg):
    print("helo task", arg)
