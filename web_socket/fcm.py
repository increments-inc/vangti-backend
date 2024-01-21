import os
import firebase_admin
from firebase_admin import credentials, messaging, auth
from django.conf import settings
# cred = credentials.Certificate(os.path.join(settings.BASE_DIR, "credentials.json"))
# firebase_admin.initialize_app(cred)

def send_push(title, msg, registration_token, data_object):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=msg,
        ),
        data=data_object,
        tokens=registration_token
    )
    response = messaging.send_each_for_multicast(
        message
    )
    print("successfully delivered", response)


def send_otp(title, msg, registration_token, data_object):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=msg,
        ),
        data=data_object,
        tokens=registration_token
    )
    response = messaging.send_each_for_multicast(
        message
    )
    print("successfully delivered", response)


def send_phone(title, msg, registration_token, data_object):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=msg,
        ),
        data=data_object,
        tokens=registration_token
    )
    response = messaging.send_each_for_multicast(
        message
    )
    print("successfully delivered", response)
