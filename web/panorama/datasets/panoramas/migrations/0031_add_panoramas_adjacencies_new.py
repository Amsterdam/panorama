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
                    to_pano_id,

                    to_timestamp,
                    to_year,
                    distance,
                    direction,
                    to_pitch - (
                        from_pitch * cos(radians(direction)) \
                        -1 * from_roll * sin(radians(direction))
                    ) AS angle,
                    to_heading AS heading,
                    to_pitch AS pitch,
                    from_geolocation_2d_rd,
                    to_geolocation_2d_rd
                FROM (SELECT
                        *,
                        (360 + (to_heading::decimal - from_heading::decimal) % 360) % 360
                            AS direction,
                        degrees(atan2(elevation, distance)) AS to_pitch
                    FROM (SELECT
                        from_pano.id || '-' || to_pano.id AS id,

                        from_pano.pano_id AS from_pano_id,
                        to_pano.pano_id AS to_pano_id,

                        to_pano.timestamp AS to_timestamp,
                        EXTRACT(YEAR FROM to_pano.timestamp) AS to_year,

                        ST_Distance(geography(to_pano.geolocation),
                            geography(from_pano.geolocation)) AS distance,
                        ST_Z(to_pano.geolocation) - ST_Z(from_pano.geolocation)
                            AS elevation,
                        degrees(ST_Azimuth(geography(from_pano.geolocation),
                            geography(to_pano.geolocation))) AS to_heading,
                        from_pano.heading AS from_heading,
                        from_pano.pitch AS from_pitch,
                        from_pano.roll AS from_roll,

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
