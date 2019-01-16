from __future__ import unicode_literals

import logging

from django.conf import settings
from django.db import migrations

log = logging.getLogger(__name__)

drop_views = []

for year in reversed(settings.PREPARED_YEARS):
    drop_views.append(
        migrations.RunSQL(
            f"DROP VIEW geo_panoramas_recente_opnames_{year} CASCADE",
            f"""CREATE VIEW geo_panoramas_recente_opnames_{year} AS
SELECT
    pp.id,
    pp.pano_id as display,
    pp.roll,
    pp.pitch,
    pp.heading,
    pp.timestamp,
    '{year}' as year,
    pp._geolocation_2d AS geometrie,
    'https://data.amsterdam.nl/panorama/' || pp.path || trim(trailing '.jpg' from pp.filename)
    || '/equirectangular/panorama_8000.jpg' AS url,
    '{settings.DATAPUNT_API_URL}' || 'panorama/recente_opnames/{year}/' || pp.pano_id || '/' AS uri
FROM
    panoramas_recent_{year} pp
WHERE
    pp.geolocation IS NOT NULL""",
        )
    )

drop_views.extend([
    migrations.RunSQL(
        "DROP VIEW geo_panoramas_panoramafotopunt CASCADE",
        f"""CREATE VIEW geo_panoramas_panoramafotopunt AS
SELECT
    pp.id,
    pp.pano_id as display,
    pp.roll,
    pp.pitch,
    pp.heading,
    pp.timestamp,
    pp.geolocation AS geometrie,
    'https://data.amsterdam.nl/panorama/' || pp.path || trim(trailing '.jpg' from pp.filename)
    || '/equirectangular/panorama_8000.jpg' AS url,
    '{settings.DATAPUNT_API_URL}' || 'panorama/opnamelocatie/' || pp.pano_id || '/' AS uri
FROM
    panoramas_panorama pp
WHERE
    pp.geolocation IS NOT NULL""",
    ),
    migrations.RunSQL(
        "DROP VIEW geo_panoramas_recente_opnames_alle CASCADE",
        f"""CREATE VIEW geo_panoramas_recente_opnames_alle AS
SELECT
    pp.id,
    pp.pano_id as display,
    pp.roll,
    pp.pitch,
    pp.heading,
    pp.timestamp,
    extract(year from pp.timestamp) as year,
    pp._geolocation_2d AS geometrie,
    'https://data.amsterdam.nl/panorama/' || pp.path || trim(trailing '.jpg' from pp.filename)
    || '/equirectangular/panorama_8000.jpg' AS url,
    '{settings.DATAPUNT_API_URL}' || 'panorama/recente_opnames/alle/' || pp.pano_id || '/' AS uri
FROM
    panoramas_recent_all pp
WHERE
    pp.geolocation IS NOT NULL
""",
    )
])

class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0005_configurable_urls')
    ]

    operations = drop_views
