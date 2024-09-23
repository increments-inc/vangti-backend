from django.core.management.base import BaseCommand, CommandError

from transactions.models import TransactionAsProviderReview, TransactionAsSeekerReview


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(f"starting batch processing of transaction review...")
        print(f"---TransactionAsProviderReview starts---")
        all_txn_prov_review = TransactionAsProviderReview.objects.all()

        for txn_prov in all_txn_prov_review:
            txn_prov.seeker = txn_prov.transaction.seeker
            txn_prov.save()
            print(f"txn updated for {txn_prov.seeker}")

        print(f"---TransactionAsSeekerReview starts---")
        all_txn_seek_review = TransactionAsSeekerReview.objects.all()

        for txn_seek in all_txn_seek_review:
            txn_seek.provider = txn_seek.transaction.provider
            txn_seek.save()
            print(f"txn updated for {txn_seek.provider}")
        print(f"...ending batch processing of transaction review")

