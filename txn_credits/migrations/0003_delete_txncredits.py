# Generated by Django 4.2.7 on 2024-09-25 10:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("txn_credits", "0002_accumulatedcredits_credituser_txncredits_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TxnCredits",
        ),
    ]
