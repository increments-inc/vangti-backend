# Generated by Django 4.2.7 on 2024-02-29 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0021_remove_usertransactionresponse_request_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertransactionresponse',
            name='response_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
