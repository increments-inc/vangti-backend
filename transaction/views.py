from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings


def send_email(user):
    host_user = settings.EMAIL_HOST_USER

    send_mail(
        "Vangti OTP",
        f"dummy mail {user}",
        host_user,
        [host_user],
        fail_silently=False,
    )
    input_letter = input("enter a number")
    return


def transaction_request_method(user_list):

    for user in user_list:
        send_email(user)

    return
