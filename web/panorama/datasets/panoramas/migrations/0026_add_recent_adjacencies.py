from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings
from geo_views import migrate

adjacency_views_per_year = []

for year in settings.PREPARED_YEARS:
    adjacency_views_per_year.append(
        migrate.ManageView(
            view_name=f"panoramas_adjacencies_recent_{year}",
            sql=f"""
SELECT * FROM panoramas_adjacencies pa
WHERE EXISTS (
    SELECT * FROM panoramas_recent_{year} pr
    WHERE pr.id = pa.from_pano_id
) AND EXISTS (
    SELECT * FROM panoramas_recent_{year} pr
    WHERE pr.id = pa.to_pano_id
)
"""
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ('panoramas', '0025_rewrite_adjacency_mv')
    ]

    operations = [
                     migrate.ManageView(
                         view_name="panoramas_adjacencies_recent_all",
                         sql="""
SELECT * FROM panoramas_adjacencies pa
WHERE EXISTS (
    SELECT * FROM panoramas_recent_all pr
    WHERE pr.id = pa.from_pano_id
) AND EXISTS (
    SELECT * FROM panoramas_recent_all pr
    WHERE pr.id = pa.to_pano_id
)
"""
                     ),
                 ] + adjacency_views_per_year
