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
from transactions.models import UserTransactionResponse
from datetime import datetime, timedelta
from users.models import User

@shared_task
def post_timestamp( seeker, provider):
    print("seeker timestamp")
    try:
        seeker = User.objects.get(id = seeker)
        provider = User.objects.get(id = provider)

        try:
            print("seeker timestamp")

            txn_response = UserTransactionResponse.objects.get(
                seeker = seeker,
                provider = provider,
                created_at__gte = datetime.now()-timedelta(minutes=5)
            )

        except UserTransactionResponse.DoesNotExist:
            print("ghsdsd hibi")
            txn_response = UserTransactionResponse.objects.create(
                seeker=seeker,
                provider=provider
            )
    except:
        print("jibi")
        return
@shared_task
def update_timestamp(seeker, provider):
    try:
        seeker = User.objects.get(id = seeker)
        provider = User.objects.get(id = provider)
        try:
            print("response timestamp")
            txn_response = UserTransactionResponse.objects.filter(
                seeker=seeker,
                provider=provider,
                # created_at__gte=datetime.now() - timedelta(minutes=5),
                # response_time= None
            ).last()
            print("timestamp resp",txn_response)
            txn_response.response_time = datetime.now()
            txn_response.save()
        except:
            print("except response timestamp")

            # txn_response = UserTransactionResponse.objects.create(
            #     seeker_id=seeker,
            #     provider_id=provider
            # )
            pass
    except:
        print("in respose exceptsdjhfsjd")
        return

    # seeker = User.objects.get(id = seeker)
    # provider = User.objects.get(id = provider)
    # print("response timestamp")
    # txn_response = UserTransactionResponse.objects.filter(
    #     seeker=seeker,
    #     provider=provider,
    #     # created_at__gte=datetime.now() - timedelta(minutes=5),
    #     # response_time= None
    # ).last()
    # print("timestamp resp",txn_response)
    # txn_response.response_time = datetime.now()
    # txn_response.save()
