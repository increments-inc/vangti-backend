from django.dispatch import receiver
from .models import *
from django.db.models.signals import post_save, pre_save
import pyotp
import time
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail


from django.conf import settings
from datetime import datetime, timedelta

@receiver(post_save, sender=User)
def create_instance(sender, instance, created, **kwargs):
    if created:
        time_now = datetime.now()
        expires = time_now + timedelta(seconds=300)
        secret_key = settings.SECRET_KEY
        base_otp = pyotp.TOTP('base32secret3232').now()

        OTPModel.objects.create(
            user=instance, 
            key=base_otp,
            expires_at=expires
        )
        host_user = settings.EMAIL_HOST_USER
        send_mail(
            "Vangti OTP",
            f"Dear Customer,\nYour One-Time-Password for Vangti app is {base_otp}\nRegards,\nVangti Team",
            host_user,
            [instance.email],
            fail_silently=False,
        )
