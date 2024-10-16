from django.core.management.base import BaseCommand, CommandError

from transactions.models import *
from txn_credits.models import CreditUser, ProviderTxnPlatform
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):

        all_txn = Transaction.objects.filter(is_completed=True)
        for txn in all_txn:
            try:
                try:
                    prov = CreditUser.objects.using("credits").get(
                        user_uid=txn.provider.id
                    )
                except CreditUser.DoesNotExist:
                    prov = CreditUser.objects.using("credits").create(
                        user_uid=txn.provider.id
                    )
                ProviderTxnPlatform.objects.using("credits").create(
                    transaction=txn.id,
                    provider=prov,
                    profit=txn.charge,
                    platform_fee=(txn.charge * settings.PLATFORM_CHARGE)
                )
                self.stdout.write(
                    self.style.SUCCESS(f"credit added for {txn.provider}"))
            except:
                self.stdout.write(
                    self.style.ERROR(f"ERROR !!!!!  {txn.provider}"))
