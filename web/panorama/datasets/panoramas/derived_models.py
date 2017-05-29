from django.db import models
from . models import AbstractPanorama, AbstractAdjacency
from django.conf import settings


class RecentPanorama(AbstractPanorama):
    class Meta(AbstractPanorama.Meta):
        abstract = False
        managed = False
        db_table = "panoramas_recent_all"


class RecentAdjacency(AbstractAdjacency):
    from_pano = models.ForeignKey(RecentPanorama, related_name='to_adjacency')
    to_pano = models.ForeignKey(RecentPanorama, related_name='from_adjacency')

    class Meta(AbstractAdjacency.Meta):
        abstract = False
        db_table = "panoramas_adjacencies_recent_all"


for year in settings.PREPARED_YEARS:
    exec(f"""
class RecentPanorama{year}(AbstractPanorama):
    class Meta(AbstractPanorama.Meta):
        abstract = False
        managed = False
        db_table = "panoramas_recent_{year}"


class RecentAdjacency{year}(AbstractAdjacency):
    from_pano = models.ForeignKey(RecentPanorama{year}, related_name='to_adjacency')
    to_pano = models.ForeignKey(RecentPanorama{year}, related_name='from_adjacency')

    class Meta(AbstractAdjacency.Meta):
        abstract = False
        db_table = "panoramas_adjacencies_recent_{year}"
    """)
