from django.conf import settings
from django.db.models import Q
from transactions.models import Transaction
from users.models import User
from utils.apps.transaction import get_transaction_id

from .location import get_user_list_provider
from .analytics import calculate_user_impressions
import os


def get_user_information(user):
    return {
        "name": user.user_info.person_name if getattr(user, "user_info", None) is not None else None,

        "picture": {
            "url": f"{settings.DOMAIN_NAME}{user.user_info.profile_pic.url}" if getattr(user, "user_info",
                                                                                        None) is not None else (
                f"{settings.DOMAIN_NAME}/media/avatars/1.png" if os.path.exists(
                    f"{os.path.abspath(os.getcwd())}/media/avatars/1.png") else None),
            "hash": user.user_info.profile_pic_hash if getattr(user, "user_info", None) is not None else None,
        },

        "rating": round(user.seeker_rating_user.rating, 1) if getattr(user, "seeker_rating_user", None) is not None else 5.0,

        "total_deals": user.seeker_rating_user.no_of_transaction if getattr(user, "seeker_rating_user", None) is not None else 0

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


def get_providers(user):
    providers = get_user_list_provider(user)

    prov_list = [
        x[0] for x in
        sorted(
            [(user.id, calculate_user_impressions(user)) for user in providers],
            key=lambda x: x[1], reverse=True
        )]
    # prov_list = list(provs.filter(
    #     "userrating_user__rating"
    # ).values_list(
    #     'id', flat=True
    # ))

    on_going_txn = list(Transaction.objects.filter(
        Q(seeker__in=prov_list) | Q(provider__in=prov_list)
    ).filter(
        is_completed=False
    ).values_list('seeker_id', 'provider_id'))

    on_going_users = [usr for user in on_going_txn for usr in user]

    user_list = [str(id_) for id_ in prov_list if id_ not in on_going_users]

    return user_list
