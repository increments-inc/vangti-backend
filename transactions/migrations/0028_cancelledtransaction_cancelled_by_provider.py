# Generated by Django 4.2.7 on 2024-03-07 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0027_remove_transactionhistory_provider_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cancelledtransaction',
            name='cancelled_by_provider',
            field=models.BooleanField(default=False),
        ),
    ]
