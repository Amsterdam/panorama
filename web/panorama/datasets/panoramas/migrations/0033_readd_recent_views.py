from __future__ import unicode_literals
from django.conf import settings

import logging

from django.db import migrations
from geo_views import migrate

log = logging.getLogger(__name__)

views_recent_pano = [
    migrate.ManageView(
        view_name="panoramas_recent_ids_all",
        sql="""
SELECT pano_id FROM panoramas_panorama p
WHERE p.status = 'done' AND p.surface_type = 'L' AND NOT EXISTS (
    SELECT * FROM panoramas_panorama n WHERE n.status = 'done' AND n.surface_type = 'L'
    AND n.timestamp > p.timestamp AND ST_DWithin(n._geolocation_2d_rd, p._geolocation_2d_rd, 4.3)
)
UNION
SELECT pano_id FROM panoramas_panorama p
WHERE p.status = 'done' AND p.surface_type = 'W' AND NOT EXISTS (
    SELECT * FROM panoramas_panorama n WHERE n.status = 'done' AND n.surface_type = 'W'
    AND n.timestamp > p.timestamp AND ST_DWithin(n._geolocation_2d_rd, p._geolocation_2d_rd, 9.3)
)
ORDER BY 1
"""
    ),
]
mvs_recent_pano = [
    migrate.ManageMaterializedView(
        view_name="panoramas_recent_all",
        sql="""
SELECT * FROM panoramas_panorama pp
WHERE EXISTS (SELECT * FROM panoramas_recent_ids_all pi WHERE pi.pano_id = pp.pano_id)
ORDER BY pp.id
"""
    ),
]
ids_mvs_recent_pano = [
    migrations.RunSQL(
        "CREATE INDEX recent_all_pano_id_idx ON public.panoramas_recent_all (pano_id) ",
        "DROP INDEX recent_all_pano_id_idx ",
    ),
    migrations.RunSQL(
        "CREATE INDEX recent_all_id_idx ON public.panoramas_recent_all (id) ",
        "DROP INDEX recent_all_pano_id_idx ",
    ),
    migrations.RunSQL(
        "CREATE INDEX recent_all_geo_2d_rd_idx ON public.panoramas_recent_all USING GIST (_geolocation_2d_rd)",
        "DROP INDEX public.recent_all_geo_2d_rd_idx"
    ),
    migrations.RunSQL(
        "CREATE INDEX recent_all_geo_2d_id ON public.panoramas_recent_all USING GIST (_geolocation_2d)",
        "DROP INDEX public.recent_all_geo_2d_id"
    ),
    migrations.RunSQL(
        "CREATE INDEX recent_all_geo_3d_id ON public.panoramas_recent_all USING GIST (geolocation)",
        "DROP INDEX public.recent_all_geo_3d_id"
    ),
]
for year in settings.PREPARED_YEARS:
    views_recent_pano.append(
        migrate.ManageView(
            view_name=f"panoramas_recent_ids_{year}",
            sql=f"""
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
ORDER BY 1
"""
        )
    )
    mvs_recent_pano.append(
        migrate.ManageMaterializedView(
            view_name=f"panoramas_recent_{year}",
            sql=f"""
SELECT * FROM panoramas_panorama pp
WHERE EXISTS (SELECT * FROM panoramas_recent_ids_{year} pi WHERE pi.pano_id = pp.pano_id)
ORDER BY pp.id
"""
        )
    )
    ids_mvs_recent_pano.extend([
        migrations.RunSQL(
            f"CREATE INDEX recent_{year}_pano_id_idx ON public.panoramas_recent_{year} (pano_id) ",
            f"DROP INDEX recent_{year}_pano_id_idx ",
        ),
        migrations.RunSQL(
            f"CREATE INDEX recent_{year}_id_idx ON public.panoramas_recent_{year} (id) ",
            f"DROP INDEX recent_{year}_pano_id_idx ",
        ),
        migrations.RunSQL(
            f"CREATE INDEX recent_{year}_geo_2d_rd_idx ON public.panoramas_recent_{year} USING GIST (_geolocation_2d_rd)",
            f"DROP INDEX public.recent_{year}_geo_2d_rd_idx"
        ),
        migrations.RunSQL(
            f"CREATE INDEX recent_{year}_geo_2d_idx ON public.panoramas_recent_{year} USING GIST (_geolocation_2d)",
            f"DROP INDEX public.recent_{year}_geo_2d_idx"
        ),
        migrations.RunSQL(
            f"CREATE INDEX recent_{year}_geo_3d_idx ON public.panoramas_recent_{year} USING GIST (geolocation)",
            f"DROP INDEX public.recent_{year}_geo_3d_idx"
        ),
    ])


class Migration(migrations.Migration):
    dependencies = [
        ('panoramas', '0032_add_tags')
    ]

    operations = views_recent_pano + mvs_recent_pano + ids_mvs_recent_pano