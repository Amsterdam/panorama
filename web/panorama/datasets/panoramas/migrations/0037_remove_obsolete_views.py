from __future__ import unicode_literals

import logging

from django.conf import settings
from django.db import migrations

log = logging.getLogger(__name__)

drop_views = []

### panoramas_adjacencies_recent_*

for year in reversed(settings.PREPARED_YEARS):
    drop_views.extend([
        migrations.RunSQL(
            f"DROP INDEX recent_adjacencies_{year}_idx ",
            f"CREATE UNIQUE INDEX recent_adjacencies_{year}_idx ON public.panoramas_adjacencies_recent_{year} (from_pano_id, to_pano_id) ",
        ),
        migrations.RunSQL(
            f"DROP MATERIALIZED VIEW panoramas_adjacencies_recent_{year} CASCADE",
            f"""CREATE MATERIALIZED VIEW panoramas_adjacencies_recent_{year} AS
SELECT * FROM panoramas_adjacencies pa
WHERE EXISTS (
    SELECT * FROM panoramas_recent_{year} pr
    WHERE pr.id = pa.from_pano_id
) AND EXISTS (
    SELECT * FROM panoramas_recent_{year} pr
    WHERE pr.id = pa.to_pano_id
)
ORDER BY pa.id"""
        ),
    ])

drop_views.extend([

    migrations.RunSQL(
        "DROP INDEX recent_adjacencies_all_idx ",
        "CREATE UNIQUE INDEX recent_adjacencies_all_idx ON public.panoramas_adjacencies_recent_all (from_pano_id, to_pano_id) ",
    ),
    migrations.RunSQL(
        "DROP MATERIALIZED VIEW panoramas_adjacencies_recent_all CASCADE",
        """CREATE MATERIALIZED VIEW panoramas_adjacencies_recent_all AS
SELECT * FROM panoramas_adjacencies pa
WHERE EXISTS (
    SELECT * FROM panoramas_recent_all pr
    WHERE pr.id = pa.from_pano_id
) AND EXISTS (
    SELECT * FROM panoramas_recent_all pr
    WHERE pr.id = pa.to_pano_id
)
ORDER BY pa.id"""
    ),
])

### panoramas_recent_*

for year in reversed(settings.PREPARED_YEARS):
    drop_views.extend([
        migrations.RunSQL(
            f"DROP INDEX recent_{year}_pano_id_idx ",
            f"CREATE INDEX recent_{year}_pano_id_idx ON public.panoramas_recent_{year} (pano_id) ",
        ),
        migrations.RunSQL(
            f"DROP INDEX recent_{year}_id_idx ",
            f"CREATE INDEX recent_{year}_id_idx ON public.panoramas_recent_{year} (id) ",
        ),
        migrations.RunSQL(
            f"DROP INDEX public.recent_{year}_geo_2d_rd_idx",
            f"CREATE INDEX recent_{year}_geo_2d_rd_idx ON public.panoramas_recent_{year} USING GIST (_geolocation_2d_rd)",
        ),
        migrations.RunSQL(
            f"DROP INDEX public.recent_{year}_geo_2d_idx",
            f"CREATE INDEX recent_{year}_geo_2d_idx ON public.panoramas_recent_{year} USING GIST (_geolocation_2d)",
        ),
        migrations.RunSQL(
            f"DROP INDEX public.recent_{year}_geo_3d_idx",
            f"CREATE INDEX recent_{year}_geo_3d_idx ON public.panoramas_recent_{year} USING GIST (geolocation)",
        ),
        migrations.RunSQL(
            f"DROP MATERIALIZED VIEW panoramas_recent_{year} CASCADE",
            f"""CREATE MATERIALIZED VIEW panoramas_recent_{year} AS
SELECT * FROM panoramas_panorama pp
WHERE EXISTS (SELECT * FROM panoramas_recent_ids_{year} pi WHERE pi.pano_id = pp.pano_id)
ORDER BY pp.id"""
        ),
    ])

### panoramas_recent_ids_*

for year in reversed(settings.PREPARED_YEARS):
    drop_views.append(
        migrations.RunSQL(
            f"DROP VIEW panoramas_recent_ids_{year} CASCADE",
            f"""CREATE VIEW panoramas_recent_ids_{year} AS
SELECT pano_id FROM panoramas_panorama p
WHERE p.status = 'done' AND p.surface_type = 'L' AND EXTRACT(year from p.timestamp) = {year} AND NOT EXISTS (
    SELECT * FROM panoramas_panorama n WHERE n.status = 'done' AND n.mission_type = 'L'
    AND EXTRACT(year from n.timestamp) = {year} AND n.timestamp > p.timestamp
    AND ST_DWithin(n._geolocation_2d_rd, p._geolocation_2d_rd, 4.3)
)
UNION
SELECT pano_id FROM panoramas_panorama p
WHERE p.status = 'done' AND p.surface_type = 'W' AND EXTRACT(year from p.timestamp) = {year} AND NOT EXISTS (
    SELECT * FROM panoramas_panorama n WHERE n.status = 'done' AND n.mission_type = 'W'
    AND EXTRACT(year from n.timestamp) = {year} AND n.timestamp > p.timestamp
    AND ST_DWithin(n._geolocation_2d_rd, p._geolocation_2d_rd, 9.3)
)
ORDER BY 1"""
        )
    )

### panoramas_adjacencies
drop_views.extend([

    migrations.RunSQL(
        "DROP INDEX from_pano_idx ",
        "CREATE INDEX from_pano_idx ON public.panoramas_adjacencies (from_pano_id, to_pano_id) ",
    ),
    migrations.RunSQL(
        "DROP INDEX from_pano_distance_idx ",
        "CREATE INDEX from_pano_distance_idx ON public.panoramas_adjacencies (from_pano_id, distance) ",
    ),
    migrations.RunSQL(
        f"DROP MATERIALIZED VIEW panoramas_adjacencies CASCADE",
        f"""CREATE MATERIALIZED VIEW panoramas_adjacencies AS
SELECT row_number() OVER (ORDER BY pp.id, pp1.id) AS id,
  pp.id AS from_pano_id,
  pp1.id AS to_pano_id,
  EXTRACT(YEAR FROM pp1.timestamp) AS to_year,
  degrees(st_azimuth(geography(pp.geolocation), geography(pp1.geolocation))) AS heading,
  st_distance(geography(pp.geolocation), geography(pp1.geolocation)) AS distance,
  st_z(pp1.geolocation) - st_z(pp.geolocation) AS elevation
FROM panoramas_panorama pp,
    panoramas_panorama pp1
WHERE ST_DWithin(pp._geolocation_2d_rd, pp1._geolocation_2d_rd, 22) AND pp1.id <> pp.id
ORDER BY pp.id, pp1.id"""
    ),

])

class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0006_remove_obsolete_views'),
        ('panoramas', '0036_add_panoramas_adjacencies_new')
    ]

    operations = drop_views
