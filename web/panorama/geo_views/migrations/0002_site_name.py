# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Packages
from django.db import migrations
from django.conf import settings


def create_site(apps, *args, **kwargs):
    Site = apps.get_model('sites', 'Site')
    Site.objects.create(
        domain=settings.DATAPUNT_API_URL,
        name='API Domain'
    )


def delete_site(apps, *args, **kwargs):
    Site = apps.get_model('sites', 'Site')
    Site.objects.filter(name='API Domain').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(code=create_site, reverse_code=delete_site)
    ]
