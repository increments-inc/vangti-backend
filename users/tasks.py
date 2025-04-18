from core.celery import app
from celery import shared_task

from .models import *
from datetime import datetime
from utils.apps.location import get_user_list
from utils.apps.analytics import get_home_analytics_of_user_set
from utils.log import logger
from utils.apps.web_socket import send_message_to_user


@app.task
def user_deletion_routine_task():
    users_to_be_deleted = UsersDeletionSchedule.objects.all()
    users_to_be_deleted_final = list(users_to_be_deleted.filter(
        user__is_active=False,
        time_of_deletion=datetime.now().date()
    ).values_list('user__id', flat=True))
    logger.info("users to be deleted %s", users_to_be_deleted_final)
    user_deleted = User.objects.filter(id__in=users_to_be_deleted_final).delete()
    users_to_be_deleted.delete()
    logger.info("users has been deleted %s", user_deleted)


@shared_task
def send_own_users_home_analytics(user):
    user_set = get_user_list(user)
    rate_data = get_home_analytics_of_user_set(user_set)
    message = {
        "request": "ANALYTICS",
        "status": "ACTIVE",
        'data': rate_data
    }
    send_message_to_user(user, message)
    pass
