# Generated by Django 4.2.7 on 2024-01-18 07:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0010_alter_transaction_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transactionrequest',
            old_name='request_status',
            new_name='status',
        ),
    ]
