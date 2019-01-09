from __future__ import unicode_literals

import logging

from django.db import migrations
from geo_views import migrate

log = logging.getLogger(__name__)


class Migration(migrations.Migration):
    dependencies = [
        ('panoramas', '0035_add_panoramas_indices')
    ]

    operations = [
        migrate.ManageView(
            view_name="panoramas_adjacencies_new",
            sql="""
                SELECT
                    id,
                    from_pano_id,
                    to_pano_id AS pano_id,

                    to_filename AS filename,
                    to_path AS path,
                    to_surface_type AS surface_type,
                    to_mission_type AS mission_type,
                    to_mission_distance AS mission_distance,
                    to_mission_year AS mission_year,
                    to_tags AS tags,
                    to_timestamp AS timestamp,

                    to_status AS status,
                    to_status_changed AS status_changed,

                    relative_distance,
                    relative_heading,
                    relative_pitch,
                    relative_elevation,

                    from_geolocation_2d_rd,

                    to_geolocation_2d_rd AS _geolocation_2d_rd,
                    to_geolocation_2d AS _geolocation_2d,
                    to_geolocation AS geolocation
                FROM (SELECT
                        *,
                        degrees(atan2(relative_elevation, relative_distance)) AS relative_pitch
                    FROM (SELECT
                        from_pano.id || '-' || to_pano.id AS id,

                        from_pano.pano_id AS from_pano_id,
                        to_pano.pano_id AS to_pano_id,

                        to_pano.filename AS to_filename,
                        to_pano.path AS to_path,
                        to_pano.surface_type AS to_surface_type,
                        to_pano.mission_type AS to_mission_type,
                        to_pano.mission_distance AS to_mission_distance,
                        to_pano.mission_year AS to_mission_year,
                        to_pano.tags AS to_tags,
                        to_pano.timestamp AS to_timestamp,

                        to_pano.status AS to_status,
                        to_pano.status_changed AS to_status_changed,

                        ST_Distance(geography(to_pano.geolocation),
                            geography(from_pano.geolocation)) AS relative_distance,
                        degrees(ST_Azimuth(geography(from_pano.geolocation),
                            geography(to_pano.geolocation))) AS relative_heading,
                        ST_Z(to_pano.geolocation) - ST_Z(from_pano.geolocation)
                            AS relative_elevation,

                        from_pano._geolocation_2d_rd AS from_geolocation_2d_rd,

                        to_pano._geolocation_2d_rd AS to_geolocation_2d_rd,
                        to_pano._geolocation_2d AS to_geolocation_2d,
                        to_pano.geolocation AS to_geolocation
                    FROM
                        panoramas_panorama from_pano,
                        panoramas_panorama to_pano
                    WHERE
                        to_pano.status = 'done'
                    ) subquery1 ) subquery2
            """
        )
    ]
