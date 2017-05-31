from __future__ import unicode_literals

import logging

from django.conf import settings
from django.db import migrations

log = logging.getLogger(__name__)

views_to_drop = [
    migrations.RunSQL(
        "DROP VIEW panoramas_adjacencies_recent_all CASCADE",
        """CREATE VIEW panoramas_adjacencies_recent_all AS
SELECT * FROM panoramas_adjacencies pa
WHERE EXISTS (
    SELECT * FROM panoramas_recent_all pr
    WHERE pr.id = pa.from_pano_id
) AND EXISTS (
    SELECT * FROM panoramas_recent_all pr
    WHERE pr.id = pa.to_pano_id
)""",
    ),
    migrations.RunSQL(
        "DROP VIEW panoramas_recent_all CASCADE",
        """CREATE VIEW panoramas_recent_all AS
SELECT * FROM panoramas_panorama pp
WHERE EXISTS (SELECT * FROM panoramas_recent_ids_all pi WHERE pi.pano_id = pp.pano_id)""",
    ),
    migrations.RunSQL(
        "DROP INDEX recent_all_pano_id_idx ",
        "CREATE INDEX recent_all_pano_id_idx ON public.panoramas_recent_ids_all (pano_id) ",
    ),
]
mvs_to_drop = [
    migrations.RunSQL(
        "DROP MATERIALIZED VIEW panoramas_recent_ids_all CASCADE",
        """CREATE MATERIALIZED VIEW panoramas_recent_ids_all AS
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
""",
    )
]

for year in settings.PREPARED_YEARS:
    views_to_drop.extend([
        migrations.RunSQL(
            f"DROP VIEW panoramas_adjacencies_recent_{year} CASCADE",
            f"""CREATE VIEW panoramas_adjacencies_recent_{year} AS
SELECT * FROM panoramas_adjacencies pa
WHERE EXISTS (
    SELECT * FROM panoramas_recent_{year} pr
    WHERE pr.id = pa.from_pano_id
) AND EXISTS (
    SELECT * FROM panoramas_recent_{year} pr
    WHERE pr.id = pa.to_pano_id
)""",
        ),
        migrations.RunSQL(
            f"DROP VIEW panoramas_recent_{year} CASCADE",
            f"""CREATE VIEW panoramas_recent_{year} AS
SELECT * FROM panoramas_panorama pp
WHERE EXISTS (SELECT * FROM panoramas_recent_ids_{year} pi WHERE pi.pano_id = pp.pano_id)"""
        ),
        migrations.RunSQL(
            f"DROP INDEX recent_{year}_pano_id_idx ",
            f"CREATE INDEX recent_{year}_pano_id_idx ON public.panoramas_recent_ids_{year} (pano_id) ",
        ),
    ])
    mvs_to_drop.extend([
        migrations.RunSQL(
            f"DROP MATERIALIZED VIEW panoramas_recent_ids_{year} CASCADE",
            f"""CREATE MATERIALIZED VIEW panoramas_recent_ids_{year} AS
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
""",
        )
    ])


class Migration(migrations.Migration):
    dependencies = [
        ('panoramas', '0027_add_readonly_models'),
        ('geo_views', '0003_add_recent')
    ]

    operations = views_to_drop + mvs_to_drop
