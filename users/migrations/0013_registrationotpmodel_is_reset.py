# Generated by Django 4.2.7 on 2024-02-27 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_userfirebasetoken_device_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationotpmodel',
            name='is_reset',
            field=models.BooleanField(default=False),
        ),
    ]
