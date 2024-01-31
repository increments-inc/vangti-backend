from firebase_admin import credentials, messaging, auth
from users.models import UserFirebaseToken
from datetime import datetime, timedelta


def send_push2(sender, receiver, data):
    token = UserFirebaseToken.objects.filter(user=sender).order_by(
        "-created_at").values_list("firebase_token", flat=True).distinct()
    print(token)
    amount = 0
    preferred_notes = []
    registration_token = [token]
    if "amount" in data:
        amount = float(data["amount"])
    if "preferred_notes" in data:
        preferred_notes = data["preferred_notes"]

    for tok in list(set(list(token))):
        print(12, tok)
        try:
            message = messaging.Message(
                data={
                    'title': 'Vangti Request',
                    'body': f'A new request has been made for {amount} and preferred notes are {preferred_notes}'
                },
                notification=messaging.Notification(
                    'Vangti Request',
                    f'A new request has been made for {amount} and preferred notes are {preferred_notes}'
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
            print("successfully delivered", response)
        except:
            print("error sending")
    return


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
    return
