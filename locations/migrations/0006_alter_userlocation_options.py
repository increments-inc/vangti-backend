# Generated by Django 4.2.7 on 2024-01-10 06:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0005_alter_userlocation_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userlocation',
            options={'ordering': ('user',)},
        ),
    ]
