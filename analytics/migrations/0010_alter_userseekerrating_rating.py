# Generated by Django 4.2.7 on 2024-03-05 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0009_userseekerrating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userseekerrating',
            name='rating',
            field=models.FloatField(default=5.0),
        ),
    ]
