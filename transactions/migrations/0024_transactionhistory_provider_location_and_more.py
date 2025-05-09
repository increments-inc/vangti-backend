# Generated by Django 4.2.7 on 2024-03-04 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0023_usertransactionresponse_response_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionhistory',
            name='provider_location',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='transactionhistory',
            name='seeker_location',
            field=models.JSONField(default=dict),
        ),
    ]
