# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-27 11:30
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Panorama',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('filename', models.CharField(max_length=255)),
                ('path', models.CharField(max_length=400)),
                ('opnamelocatie', django.contrib.gis.db.models.fields.PointField(dim=3, srid=4326)),
                ('roll', models.FloatField(null=True)),
                ('pitch', models.FloatField(null=True)),
                ('heading', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Traject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('opnamelocatie', django.contrib.gis.db.models.fields.PointField(dim=3, srid=4326)),
                ('north_rms', models.DecimalField(decimal_places=14, max_digits=20, null=True)),
                ('east_rms', models.DecimalField(decimal_places=14, max_digits=20, null=True)),
                ('down_rms', models.DecimalField(decimal_places=14, max_digits=20, null=True)),
                ('roll_rms', models.FloatField(null=True)),
                ('pitch_rms', models.FloatField(null=True)),
                ('heading_rms', models.FloatField(null=True)),
            ],
        ),
    ]
