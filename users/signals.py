from django.dispatch import receiver
from .models import *
from django.db.models.signals import post_save, pre_save, post_delete
from transactions.models import UserServiceMode
from locations.models import UserLocation
from analytics.models import UserRating
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed
)


@receiver(post_save, sender=User)
def create_instance(sender, instance, created, **kwargs):
    if created:
        try:
            # user infos
            UserInformation.objects.create(
                user=instance
            )
            UserNidInformation.objects.create(
                user=instance
            )
            # user service
            UserServiceMode.objects.create(
                user=instance
            )
            # location
            UserLocation.objects.create(
                user=instance.id,
                user_phone_number=instance.phone_number,
            )
            # analytics rating
            UserRating.objects.create(
                user=instance
            )
        except:
            pass


@receiver(post_delete, sender=User)
def delete_instance(sender, instance, **kwargs):
    # print(kwargs["origin"], instance.id, instance.phone_number)
    try:
        UserLocation.objects.filter(
            user_phone_number=instance.phone_number,
        ).delete()
    except:
        pass


# @receiver(user_logged_in)
# def log_user_login(sender, request, user, **kwargs):
#     print('user logged in')
#
#
# @receiver(user_login_failed)
# def log_user_login_failed(sender, credentials, request, **kwargs):
#     print('user logged in failed')
#
#
# @receiver(user_logged_out)
# def log_user_logout(sender, request, user, **kwargs):
#     print('user logged out')
