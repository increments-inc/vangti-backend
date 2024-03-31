from users.models import UserInformation, UserNidInformation, User
from transactions.models import UserServiceMode
from locations.models import UserLocation
from analytics.models import UserRating


def default_user_models(user):
    # user info
    try:
        UserInformation.objects.get(
            user=user
        )
    except UserInformation.DoesNotExist:
        UserInformation.objects.create(
            user=user
        )
    # user nid
    try:
        UserNidInformation.objects.get(
            user=user
        )
    except UserNidInformation.DoesNotExist:
        UserNidInformation.objects.create(
            user=user
        )
    # user service
    try:
        UserServiceMode.objects.get(
            user=user
        )
    except UserServiceMode.DoesNotExist:
        UserServiceMode.objects.create(
            user=user
        )
    # location
    try:
        UserLocation.objects.get(
            user=user.id,
            user_phone_number=user.phone_number,
        )
    except UserLocation.DoesNotExist:
        UserLocation.objects.create(
            user=user.id,
            user_phone_number=user.phone_number,
        )
    # rating
    try:
        UserRating.objects.get(
            user=user
        )
    except UserRating.DoesNotExist:
        UserRating.objects.create(
            user=user
        )
    return
