from django.db import models
from . models import AbstractPanorama, AbstractAdjacency


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
