# Generated by Django 4.2.7 on 2024-02-10 06:48

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0010_polyline_alter_userlocation_latitude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='polyline',
            name='point',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='polyline',
            name='linestring',
            field=django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=4326),
        ),
    ]
