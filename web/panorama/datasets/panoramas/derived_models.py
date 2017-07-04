from django.db import models
from . models import AbstractPanorama, AbstractAdjacency
from django.conf import settings


def _find_set(path):
    recent_db_table_suffix = ['all']
    recent_db_table_suffix.extend(settings.PREPARED_YEARS)

    for set in recent_db_table_suffix:
        if f'recente_opnames/{set}' in path:
            return set


def getRecentPanoModel(path):
    set = _find_set(path)
    db_table_name = f"panoramas_recent_{set}"

    class RecentPanorama(AbstractPanorama):
        class Meta(AbstractPanorama.Meta):
            abstract = False
            managed = False
            db_table = db_table_name

    return RecentPanorama


def getRecentAdjacencyModel(recent_pano_model, path):
    set = _find_set(path)
    db_table_name = f"panoramas_adjacencies_recent_{set}"

    class RecentAdjacency(AbstractAdjacency):
        from_pano = models.ForeignKey(recent_pano_model, related_name='to_adjacency')
        to_pano = models.ForeignKey(recent_pano_model, related_name='from_adjacency')

        class Meta(AbstractAdjacency.Meta):
            abstract = False
            db_table = db_table_name

    return RecentAdjacency
