# Generated by Django 4.2.7 on 2024-01-17 04:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_userfirebasetoken_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfirebasetoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_firebase_token', to=settings.AUTH_USER_MODEL),
        ),
    ]
