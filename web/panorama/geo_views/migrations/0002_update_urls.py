from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('geo_views', '0001_initial'),
    ]

    operations = [
        migrate.ManageView(
            view_name="geo_panoramas_panoramafotopunt",
            sql=f"""
SELECT
    pp.id,
    pp.pano_id as display,
    pp.roll,
    pp.pitch,
    pp.heading,
    pp.timestamp,
    pp.geolocation AS geometrie,
    'https://atlas.amsterdam.nl/panorama/' || pp.path || trim(trailing '.jpg' from pp.filename)
    || '/equirectangular/panorama_8000.jpg' AS url,
    '{settings.DATAPUNT_API_URL}' || 'panorama/opnamelocatie/' || pp.pano_id || '/' AS uri
FROM
    panoramas_panorama pp
WHERE
    pp.geolocation IS NOT NULL
"""
        ),
    ]
