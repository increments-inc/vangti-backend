# Generated by Django 4.2.7 on 2023-12-24 06:20

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.CharField(blank=True, max_length=10, null=True)),
                ('longitude', models.CharField(blank=True, max_length=10, null=True)),
                ('loc', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_location', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LocationRadius',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_list', models.JSONField()),
                ('user_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_location_radius', to='web_socket.userlocation')),
            ],
        ),
    ]
