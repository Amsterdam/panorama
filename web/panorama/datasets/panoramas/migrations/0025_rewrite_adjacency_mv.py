from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate


class Migration(migrations.Migration):

    dependencies = [
        ('panoramas', '0024_add_recent_panorama_views')
    ]

    operations = [
        migrate.ManageMaterializedView(
            view_name="panoramas_adjacencies",
            sql="""
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
        migrations.RunSQL(
            "CREATE INDEX from_pano_idx ON public.panoramas_adjacencies (from_pano_id, to_pano_id) ",
            "DROP INDEX from_pano_idx ",
        ),
        migrations.RunSQL(
            "CREATE INDEX from_pano_distance_idx ON public.panoramas_adjacencies (from_pano_id, distance) ",
            "DROP INDEX from_pano_distance_idx ",
        ),
    ]
