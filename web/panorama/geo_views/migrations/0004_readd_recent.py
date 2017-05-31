from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate
from django.conf import settings

geo_views_per_year = []
for year in settings.PREPARED_YEARS:
    geo_views_per_year.append(
        migrate.ManageView(
            view_name=f"geo_panoramas_recente_opnames_{year}",
            sql=f"""
SELECT
    pp.id,
    pp.pano_id as display,
    pp.roll,
    pp.pitch,
    pp.heading,
    pp.timestamp,
    '{year}' as year,
    pp._geolocation_2d AS geometrie,
    'https://atlas.amsterdam.nl/panorama/' || pp.path || trim(trailing '.jpg' from pp.filename)
    || '/equirectangular/panorama_8000.jpg' AS url,
    '{settings.DATAPUNT_API_URL}' || 'panorama/recente_opnames/{year}/' || pp.pano_id || '/' AS uri
FROM
    panoramas_recent_{year} pp
WHERE
    pp.geolocation IS NOT NULL
"""
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0003_add_recent'),
        ('panoramas', '0030_readd_recent_adjacencies')
    ]

    operations = [
                     migrate.ManageView(
                         view_name="geo_panoramas_recente_opnames_alle",
                         sql=f"""
SELECT
    pp.id,
    pp.pano_id as display,
    pp.roll,
    pp.pitch,
    pp.heading,
    pp.timestamp,
    extract(year from pp.timestamp) as year,
    pp._geolocation_2d AS geometrie,
    'https://atlas.amsterdam.nl/panorama/' || pp.path || trim(trailing '.jpg' from pp.filename)
    || '/equirectangular/panorama_8000.jpg' AS url,
    '{settings.DATAPUNT_API_URL}' || 'panorama/recente_opnames/alle/' || pp.pano_id || '/' AS uri
FROM
    panoramas_recent_all pp
WHERE
    pp.geolocation IS NOT NULL
"""
                     ),
                 ] + geo_views_per_year
