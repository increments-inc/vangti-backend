# Generated by Django 4.2.7 on 2024-01-11 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0007_remove_transactionrequest_is_affirmed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userservicemode',
            options={'ordering': ('user',)},
        ),
    ]
