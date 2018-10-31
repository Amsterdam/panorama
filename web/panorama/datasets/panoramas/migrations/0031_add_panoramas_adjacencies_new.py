from __future__ import unicode_literals
from django.conf import settings

import logging

from django.db import migrations
from geo_views import migrate

log = logging.getLogger(__name__)

class Migration(migrations.Migration):
    dependencies = [
        ('panoramas', '0030_readd_recent_adjacencies')
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
                    to_status AS status,
                    to_status_changed AS status_changed,
                    to_mission_type AS mission_type,

                    to_timestamp AS timestamp,

                    relative_distance,
                    relative_direction,

                    to_roll AS roll,

                    to_pitch - (
                        from_pitch * cos(radians(relative_direction)) \
                        -1 * from_roll * sin(radians(relative_direction))
                    ) AS relative_angle,

                    to_heading AS heading,
                    relative_heading,

                    to_pitch AS pitch,

                    from_geolocation_2d_rd,

                    to_geolocation_2d_rd AS _geolocation_2d_rd,
                    to_geolocation_2d AS _geolocation_2d,

                    to_geolocation AS geolocation
                FROM (SELECT
                        *,
                        (360 + (to_heading::decimal - from_heading::decimal) % 360) % 360
                            AS relative_direction,
                        degrees(atan2(relative_elevation, relative_distance)) AS relative_pitch
                    FROM (SELECT
                        from_pano.id || '-' || to_pano.id AS id,

                        from_pano.pano_id AS from_pano_id,
                        to_pano.pano_id AS to_pano_id,

                        to_pano.filename AS to_filename,
                        to_pano.mission_type AS to_mission_type,

                        to_pano.path AS to_path,
                        to_pano.status AS to_status,
                        to_pano.status_changed AS to_status_changed,

                        to_pano.timestamp AS to_timestamp,

                        ST_Distance(geography(to_pano.geolocation),
                            geography(from_pano.geolocation)) AS relative_distance,
                        ST_Z(to_pano.geolocation) - ST_Z(from_pano.geolocation)
                            AS relative_elevation,

                        from_pano.heading AS from_heading,
                        to_pano.heading AS to_heading,
                        degrees(ST_Azimuth(geography(from_pano.geolocation),
                            geography(to_pano.geolocation))) AS relative_heading,

                        from_pano.pitch AS from_pitch,
                        to_pano.pitch AS to_pitch,

                        from_pano.roll AS from_roll,
                        to_pano.roll AS to_roll,

                        to_pano.geolocation AS to_geolocation,
                        to_pano._geolocation_2d AS to_geolocation_2d,

                        from_pano._geolocation_2d_rd AS from_geolocation_2d_rd,
                        to_pano._geolocation_2d_rd AS to_geolocation_2d_rd
                    FROM
                        panoramas_panorama from_pano,
                        panoramas_panorama to_pano
                    WHERE
                        to_pano.status = 'done'
                    ) a1 ) a2
            """
        )
    ]
