from django.conf import settings
from utils.apps.transaction import get_transaction_id
from transactions.models import Transaction
from locations.models import UserLocation
from users.models import User


def get_user_information(user):
    return {
        "name": user.user_info.person_name if getattr(user, "user_info", None) is not None else None,
        "picture": {
            "url": f"{settings.DOMAIN_NAME} + {user.user_info.profile_pic.url}" if getattr(user, "user_info",
                                                                                           None) is not None else None,
            "hash": user.user_info.profile_pic_hash
            if getattr(user, "user_info", None) is not None else None,
        },
        "rating": user.seeker_rating_user.rating
        if getattr(user, "seeker_rating_user", None) is not None else 5.0,
        "total_deals": user.seeker_rating_user.no_of_transaction
        if getattr(user, "seeker_rating_user", None) is not None else 0
    }


def get_transaction_instance(transaction_id):
    transaction_id = get_transaction_id(transaction_id)
    try:
        return Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return -1


def create_transaction_instance(dict_data):
    provider = User.objects.get(id=dict_data["provider"])
    seeker = User.objects.get(id=dict_data["seeker"])
    try:
        transaction_instance = Transaction.objects.get(
            provider=provider,
            seeker=seeker,
            is_completed=False
        )
        transaction_instance.total_amount = dict_data["amount"]
        transaction_instance.preferred_notes = dict_data["preferred"]
        transaction_instance.charge = settings.PROVIDER_COMMISSION
        transaction_instance.save()
    except Transaction.DoesNotExist:
        transaction_instance = Transaction.objects.create(
            total_amount=dict_data["amount"],
            preferred_notes=dict_data["preferred"],
            provider=provider,
            seeker=seeker,
            charge=settings.PROVIDER_COMMISSION
        )
    transaction_hex_id = transaction_instance.get_transaction_unique_no
    return str(transaction_hex_id)


def get_user_location(user_id):
    return
