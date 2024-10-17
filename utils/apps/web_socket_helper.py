from django.conf import settings
from django.db.models import Q
from transactions.models import Transaction, UserOnTxnRequest
from users.models import User
from utils.apps.transaction import get_transaction_id

from utils.apps.location import get_user_list_provider
from utils.apps.analytics import calculate_user_impressions

from datetime import datetime
from itertools import cycle


def get_user_information(user):
    name = ""
    profile_pic = f"{settings.DOMAIN_NAME}/media/avatars/1.png"
    pic_hash = None
    rating = 5.0
    deals = 0

    try:
        if getattr(user, "user_info", None) is not None:
            name = user.user_info.person_name
        if getattr(user, "seeker_rating_user", None) is not None:
            rating = round(user.seeker_rating_user.rating, 1)
            deals = user.seeker_rating_user.no_of_transaction
        if getattr(user, "user_info", None) is not None:
            if bool(user.user_info.profile_pic):
                profile_pic = f"{settings.DOMAIN_NAME}{user.user_info.profile_pic.url}"
            pic_hash = user.user_info.profile_pic_hash
    except:
        pass

    return {
        "name": name,
        "picture": {
            "url": profile_pic,
            "hash": pic_hash,
        },
        "rating": rating,
        "total_deals": deals
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
        transaction_instance.charge = (dict_data["amount"] * settings.PROVIDER_COMMISSION)
        transaction_instance.save()
    except Transaction.DoesNotExist:
        transaction_instance = Transaction.objects.create(
            total_amount=dict_data["amount"],
            preferred_notes=dict_data["preferred"],
            provider=provider,
            seeker=seeker,
            charge=(dict_data["amount"] * settings.PROVIDER_COMMISSION)
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


def iterate_over_cycle(user_list: list) -> list:
    print("here in iterate_over_cycle.........")
    counter = 0
    dummy_index = 0
    user_cycle = cycle(user_list)
    length_user_list = len(user_list)
    list_index = -1
    for i in user_cycle:
        list_index += 1
        if list_index == length_user_list:
            list_index = 0
        print("im iterating", i )
        if counter > 500:
            return []
        provider_on_req = UserOnTxnRequest.objects.filter(user_id=i)
        if provider_on_req.exists():
            print("found! on provider request", provider_on_req)
            counter += 1
            continue
        dummy_index = list_index
        break
    dummy_element = user_list[dummy_index]
    user_list[dummy_index] = user_list[0]
    user_list[0] = dummy_element
    return user_list
