# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-20 11:13
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.gis.db.models.fields import PointField


class Migration(migrations.Migration):

    dependencies = [
        ('panoramas', '0005_autogenerated')
    ]

    operations = [
        migrations.AddField(
            model_name='panorama',
            name='geopoint',
            field=PointField(default=None, null=True, srid=4326),
            preserve_default=False,
        ),
        migrations.RunSQL(
            "update public.panoramas_panorama set geopoint = ST_PointFromText('POINT('||st_x(geolocation)||' '||st_y(geolocation)||')', 4326)",
            "update public.panoramas_panorama set geopoint = null"
        ),
    ]
