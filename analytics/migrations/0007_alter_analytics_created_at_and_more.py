# Generated by Django 4.2.7 on 2024-01-01 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0006_userrating_provider_response_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analytics',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='analytics',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='appfeedback',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='appfeedback',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='userrating',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='userrating',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
