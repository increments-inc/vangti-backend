from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Sum, Avg

from analytics.models import UserRating, UserSeekerRating

from transactions.models import TransactionAsProviderReview, TransactionAsSeekerReview
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_users = User.objects.all()
        self.stdout.write(
                self.style.NOTICE(f"starting batch processing of user rating..."))
        for user in all_users:
            # user as provider
            try:
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
            except:
                self.stdout.write(
                self.style.ERROR(f"user{user} does not have review as provider"))

            # user as seeker
            try:
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
            except:
                self.stdout.write(
                self.style.ERROR(f"user{user} does not have review as seeker"))

            self.stdout.write(
                self.style.SUCCESS(f"rating for user {user}"))

        self.stdout.write(
                self.style.NOTICE(f"...ending batch processing of transaction review"))
