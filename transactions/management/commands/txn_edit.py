from django.core.management.base import BaseCommand, CommandError

from transactions.models import *
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        transaction_ids = TransactionHistory.objects.values_list('transaction__id', flat=True)
        all_txn = Transaction.objects.filter(id__in=transaction_ids)
        print(transaction_ids,"\n", all_txn)

        for txn in all_txn:
            txn.is_completed = False
            txn.save()
            print(f"is_completed=false for {txn}")

        for txn in all_txn:
            try:
                txn.is_completed = True
                txn.charge = (txn.total_amount * settings.PROVIDER_COMMISSION)
                txn.save()
                print(f"profit changed  for {txn.provider}")
            except:
                print(f"ERROR !!!!!  {txn.provider}")
