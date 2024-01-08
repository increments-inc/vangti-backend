import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings


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
