from __future__ import unicode_literals

import logging

from django.conf import settings
from django.db import migrations

log = logging.getLogger(__name__)


class Migration(migrations.Migration):
    dependencies = [
        ('panoramas', '0037_remove_obsolete_views')
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX panoramas_panorama_gpx ON panoramas_panorama USING GIST (geography(_geolocation_2d)) ",
            "DROP INDEX panoramas_panorama_gpx ",
        ),
    ]
