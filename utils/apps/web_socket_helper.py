from django.conf import settings
from utils.apps.transaction import get_transaction_id
from transactions.models import Transaction
from locations.models import UserLocation


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


def get_user_location(user_id):
    return
