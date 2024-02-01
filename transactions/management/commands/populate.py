from django.core.management.base import BaseCommand, CommandError
from ...models import *


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        TransactionHistory.objects.filter(
            provider=User.objects.get(phone_number="+8801234567892"),
            seeker=User.objects.get(phone_number="+8801749727797"),

        ).delete()
        TransactionHistory.objects.filter(
            seeker=User.objects.get(phone_number="+8801234567892"),
            provider=User.objects.get(phone_number="+8801749727797"),

        ).delete()
        Transaction.objects.filter(

            provider=User.objects.get(phone_number="+88012345123456"),
            seeker=User.objects.get(phone_number="+8801749727797"),

        ).delete()
        Transaction.objects.filter(
            seeker=User.objects.get(phone_number="+88012345123456"),
            provider=User.objects.get(phone_number="+8801749727797"),

        ).delete()
        TransactionHistory.objects.filter(
            provider=User.objects.get(phone_number="+88012345123456"),
            seeker=User.objects.get(phone_number="+8801749727797"),
        ).delete()
        TransactionHistory.objects.filter(
            seeker=User.objects.get(phone_number="+88012345123456"),
            provider=User.objects.get(phone_number="+8801749727797"),
        ).delete()
        for i in range(20):
            Transaction.objects.create(
                total_amount=10000,
                preferred_notes=["122"],
                provider=User.objects.get(phone_number="+8801234567892"),
                seeker=User.objects.get(phone_number="+8801749727797"),
                charge=100,
                is_completed=True
            )
        for i in range(20):
            Transaction.objects.create(
                total_amount=10000,
                preferred_notes=["122"],
                seeker=User.objects.get(phone_number="+8801234567892"),
                provider=User.objects.get(phone_number="+8801749727797"),
                charge=100,
                is_completed=True
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully closed poll "%s"')
        )
