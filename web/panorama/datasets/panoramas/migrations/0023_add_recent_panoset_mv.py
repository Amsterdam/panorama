from __future__ import unicode_literals
from django.conf import settings

import logging

from django.db import migrations
from geo_views import migrate

log = logging.getLogger(__name__)

materialized_views_per_year = []
mv_indices_per_year = []

for year in settings.PREPARED_YEARS:
    materialized_views_per_year.append(
        migrate.ManageMaterializedView(
            view_name=f"panoramas_recent_ids_{year}",
            sql=f"""
SELECT pano_id FROM panoramas_panorama p
WHERE p.status = 'done' AND p.mission_type = 'L' AND EXTRACT(year from p.timestamp) = {year} AND NOT EXISTS (
    SELECT * FROM panoramas_panorama n WHERE n.status = 'done' AND n.mission_type = 'L'
    AND EXTRACT(year from n.timestamp) = {year} AND n.timestamp > p.timestamp
    AND ST_DWithin(n._geolocation_2d_rd, p._geolocation_2d_rd, 4.5)
)
UNION
SELECT pano_id FROM panoramas_panorama p
WHERE p.status = 'done' AND p.mission_type = 'W' AND EXTRACT(year from p.timestamp) = {year} AND NOT EXISTS (
    SELECT * FROM panoramas_panorama n WHERE n.status = 'done' AND n.mission_type = 'W'
    AND EXTRACT(year from n.timestamp) = {year} AND n.timestamp > p.timestamp
    AND ST_DWithin(n._geolocation_2d_rd, p._geolocation_2d_rd, 9.5)
)
ORDER BY 1
"""
        )
    )
    mv_indices_per_year.append(
        migrations.RunSQL(
            f"CREATE INDEX recent_{year}_pano_id_idx ON public.panoramas_recent_ids_{year} (pano_id) ",
            f"DROP INDEX recent_{year}_pano_id_idx ",
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ('panoramas', '0022_add_rd_geolocation')
    ]

    operations = [
                     migrate.ManageMaterializedView(
                         view_name="panoramas_recent_ids_all",
                         sql="""
SELECT pano_id FROM panoramas_panorama p
WHERE p.status = 'done' AND p.mission_type = 'L' AND NOT EXISTS (
    SELECT * FROM panoramas_panorama n WHERE n.status = 'done' AND n.mission_type = 'L'
    AND n.timestamp > p.timestamp AND ST_DWithin(n._geolocation_2d_rd, p._geolocation_2d_rd, 4.3)
)
UNION
SELECT pano_id FROM panoramas_panorama p
WHERE p.status = 'done' AND p.mission_type = 'W' AND NOT EXISTS (
    SELECT * FROM panoramas_panorama n WHERE n.status = 'done' AND n.mission_type = 'W'
    AND n.timestamp > p.timestamp AND ST_DWithin(n._geolocation_2d_rd, p._geolocation_2d_rd, 9.5)
)
ORDER BY 1
"""
                     ),
                     migrations.RunSQL(
                         "CREATE INDEX recent_all_pano_id_idx ON public.panoramas_recent_ids_all (pano_id) ",
                         "DROP INDEX recent_all_pano_id_idx ",
                     ),
                 ] + materialized_views_per_year  + mv_indices_per_year
