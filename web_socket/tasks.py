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

from utils.apps.location import get_user_list
from utils.apps.analytics import get_home_analytics_of_user_set
from utils.apps.analytics_rating import update_response_times
from utils.apps.web_socket import send_message_to_user
from utils.fcm import send_fcm
from utils.log import logger


@shared_task
def post_timestamp(seeker, provider):
    logger.info("seeker timestamp")
    try:
        seeker = User.objects.get(id=seeker)
        provider = User.objects.get(id=provider)

        try:
            logger.info("seeker timestamp")

            txn_response = UserTransactionResponse.objects.get(
                seeker=seeker,
                provider=provider,
                created_at__gte=datetime.now() - timedelta(minutes=5)
            )

        except UserTransactionResponse.DoesNotExist:
            logger.info("ghsdsd hibi")
            txn_response = UserTransactionResponse.objects.create(
                seeker=seeker,
                provider=provider
            )
    except:
        logger.info("jibi")
        return


@shared_task
def update_timestamp(seeker, provider):
    try:
        seeker = User.objects.get(id=seeker)
        provider = User.objects.get(id=provider)
        try:
            logger.info("response timestamp")
            txn_response = UserTransactionResponse.objects.filter(
                seeker=seeker,
                provider=provider,
                # created_at__gte=datetime.now() - timedelta(minutes=5),
                # response_time= None
            ).last()
            logger.info("timestamp resp", txn_response)
            txn_response.response_time = datetime.now()
            txn_response.save()
        except:
            logger.info("except response timestamp")

            # txn_response = UserTransactionResponse.objects.create(
            #     seeker_id=seeker,
            #     provider_id=provider
            # )
            pass
    except:
        logger.info("in respose exceptsdjhfsjd")
        return

    # seeker = User.objects.get(id = seeker)
    # provider = User.objects.get(id = provider)
    # logger.info("response timestamp")
    # txn_response = UserTransactionResponse.objects.filter(
    #     seeker=seeker,
    #     provider=provider,
    #     # created_at__gte=datetime.now() - timedelta(minutes=5),
    #     # response_time= None
    # ).last()
    # logger.info("timestamp resp",txn_response)
    # txn_response.response_time = datetime.now()
    # txn_response.save()


# @shared_task
def send_own_users_home_analytics(user):
    logger.info("send own_users_home_analytics")
    user_set = get_user_list(user)
    rate_data = get_home_analytics_of_user_set(user_set)
    message = {
        "request": "ANALYTICS",
        "status": "ACTIVE",
        'data': rate_data
    }
    send_message_to_user(user, message)
    logger.info("here")
# await self.send(text_data=json.dumps({
#     'message': 'WebSocket connection established.'
# }))


@shared_task
def update_providers_timestamps(seeker_id, user_list):
    seeker = User.objects.get(id=seeker_id)
    for user_ in user_list:
        provider = User.objects.get(id=user_[0])
        duration = user_[2] - user_[1]
        UserTransactionResponse.objects.create(
            seeker=seeker,
            provider=provider,
            response_duration=duration
        )

        # rating calculation
        update_response_times(provider)

    return


@shared_task
def send_push_notif(user_id, data):
    user = User.objects.get(id=user_id)

    try:
        send_fcm(user, data)
    except Exception as e:
        pass
    return
