from django.core.management.base import BaseCommand, CommandError

from transactions.models import *
from txn_credits.models import CreditUser, ProviderTxnPlatform, AccumulatedCredits
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(settings.PLATFORM_CHARGE)
        # delete all credits
        CreditUser.objects.using("credits").delete()

        # grab all complete txn
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
                try:
                    pl_txn = ProviderTxnPlatform.objects.using("credits").get(
                        transaction=txn.id)
                    print(pl_txn, pl_txn.platform_fee)
                    print("txn", txn.charge * settings.PLATFORM_CHARGE)
                    pl_txn.platform_fee = float(txn.charge * settings.PLATFORM_CHARGE)
                    pl_txn.save()
                    print(pl_txn.platform_fee)
                    self.stdout.write(
                        self.style.SUCCESS(f" ALREADY credit added for {txn.provider}"))
                except:
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

        # check
        print(ProviderTxnPlatform.objects.using("credits").all().values("platform_fee"))
