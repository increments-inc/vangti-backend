# Generated by Django 4.2.7 on 2024-02-20 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_usersdeletionschedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='userfirebasetoken',
            name='device_token',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
