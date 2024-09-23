from firebase_admin import credentials, messaging, auth
from pyarmor.examples.testpkg.mypkg import title

from users.models import UserFirebaseToken
from datetime import datetime, timedelta


def send_fcm(user, data):
    token = UserFirebaseToken.objects.filter(
        user=user).order_by(
        "-created_at"
    ).values_list(
        "firebase_token", flat=True
    ).distinct()

    type_msg = data["request"]  # TRANSACTION, MESSAGE
    status = data["status"]  # PENDING, ACCEPTED, ON_GOING_TRANSACTION

    msg_title = ""
    body = ""

    if type_msg == "TRANSACTION":
        if status == "PENDING":
            amount = data["data"]["amount"]
            preferred_notes = data["data"]["preferred"]
            msg_title = 'Vangti Request'
            body = f'A new request has been made for {amount} and preferred notes are {preferred_notes}'
        elif status == "ACCEPTED":
            msg_title = 'Vangti Request Accepted!'
            body = f'Your vangti request has been accepted. Check Vangti app for transaction.'

    elif type_msg == "MESSAGE" and status == "ON_GOING_TRANSACTION":
        msg_title = 'New Message From Vangti Provider'
        body = f'message : {data["data"]["message"]}'

    else:
        return

    for tok in list(set(list(token))):
        try:
            message = messaging.Message(
                data={
                    'title': msg_title,
                    'body': body
                },
                notification=messaging.Notification(
                    msg_title,
                    body
                ),
                android=messaging.AndroidConfig(
                    ttl=timedelta(seconds=3600),
                    priority='normal',
                    notification=messaging.AndroidNotification(
                        icon='stock_ticker_update',
                        color='#f45342'
                    ),
                ),
                token=tok,
            )
            response = messaging.send(message)
            print(f"fcm sent to {user}")
            break
        except:
            print(f"error sending fcm to {user}")
    return
