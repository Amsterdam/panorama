from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings
from geo_views import migrate

adjacency_views = [
    migrate.ManageMaterializedView(
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
ORDER BY pa.id
"""
    ),
]
adjacency_idxs = [
    migrations.RunSQL(
        "CREATE UNIQUE INDEX recent_adjacencies_all_idx ON public.panoramas_adjacencies_recent_all (from_pano_id, to_pano_id) ",
        "DROP INDEX recent_adjacencies_all_idx ",
    ),
]

for year in settings.PREPARED_YEARS:
    adjacency_views.append(
        migrate.ManageMaterializedView(
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
ORDER BY pa.id
"""
        )
    )
    adjacency_idxs.append(
        migrations.RunSQL(
            f"CREATE UNIQUE INDEX recent_adjacencies_{year}_idx ON public.panoramas_adjacencies_recent_{year} (from_pano_id, to_pano_id) ",
            f"DROP INDEX recent_adjacencies_{year}_idx ",
        ),
    )


class Migration(migrations.Migration):
    dependencies = [
        ('panoramas', '0029_readd_recent_views')
    ]

    operations = adjacency_views + adjacency_idxs
