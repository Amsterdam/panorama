from __future__ import unicode_literals

from django.db import migrations
from geo_views import migrate

PREPARED_YEARS = range(2016, 2021)
panorama_views_per_year = []

for year in PREPARED_YEARS:
    panorama_views_per_year.append(
        migrate.ManageView(
            view_name=f"panoramas_recent_{year}",
            sql=f"""
SELECT * FROM panoramas_panorama pp
WHERE EXISTS (SELECT * FROM panoramas_recent_ids_{year} pi WHERE pi.pano_id = pp.pano_id)
"""
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ('panoramas', '0023_add_recent_panoset_mv')
    ]

    operations = [
        migrate.ManageView(
            view_name="panoramas_recent_all",
            sql="""
SELECT * FROM panoramas_panorama pp
WHERE EXISTS (SELECT * FROM panoramas_recent_ids_all pi WHERE pi.pano_id = pp.pano_id)
"""
        ),
    ] + panorama_views_per_year
