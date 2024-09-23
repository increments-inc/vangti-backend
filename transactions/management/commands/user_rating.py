from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Sum, Avg

from analytics.models import UserRating, UserSeekerRating

from transactions.models import TransactionAsProviderReview, TransactionAsSeekerReview
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_users = User.objects.all()
        print(f"starting batch processing of user rating...")
        for user in all_users:
            # user as provider
            all_reviews = TransactionAsSeekerReview.objects.filter(
                provider=user
            ).aggregate(
                Avg("rating", default=0)
            )
            user_as_prov = UserRating.objects.get(
                user=user
            )
            user_as_prov.rating = all_reviews["rating__avg"]
            user_as_prov.save()

            # user as seeker

            all_reviews = TransactionAsProviderReview.objects.filter(
                seeker=user
            ).aggregate(
                Avg("rating", default=0)
            )
            new_rating = (5 + all_reviews["rating__avg"]) / 2
            user_as_seek = UserSeekerRating.objects.get(
                user=user
            )
            user_as_seek.rating = new_rating
            user_as_seek.save()

            print(f"rating for user {user}")

        print(f"...ending batch processing of transaction review")
