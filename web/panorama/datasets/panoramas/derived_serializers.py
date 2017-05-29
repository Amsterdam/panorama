import logging
from django.conf import settings
from datasets.panoramas import derived_models as models
from . serializers import AdjacencySerializer, PanoSerializer, FilteredPanoSerializer

log = logging.getLogger(__name__)


class RecentPanoSerializer(PanoSerializer):
    class Meta(PanoSerializer.Meta):
        model = models.RecentPanorama


class RecentAdjacencySerializer(AdjacencySerializer):
    class Meta(AdjacencySerializer.Meta):
        model = models.RecentAdjacency


class FilteredRecentPanoSerializer(FilteredPanoSerializer):
    class Meta(PanoSerializer.Meta):
        model = models.RecentPanorama

    class Models(FilteredPanoSerializer.Models):
        adjacency_model = models.RecentAdjacency
        panorama_model = models.RecentPanorama
        adjacency_serializer = RecentAdjacencySerializer


for year in settings.PREPARED_YEARS:
    exec(f"""
class RecentPano{year}Serializer(PanoSerializer):
    class Meta(PanoSerializer.Meta):
        model = models.RecentPanorama{year}


class RecentAdjacency{year}Serializer(AdjacencySerializer):
    class Meta(AdjacencySerializer.Meta):
        model = models.RecentAdjacency{year}


class FilteredRecentPano{year}Serializer(FilteredPanoSerializer):
    class Meta(PanoSerializer.Meta):
        model = models.RecentPanorama{year}

    class Models(FilteredPanoSerializer.Models):
        adjacency_model = models.RecentAdjacency{year}
        panorama_model = models.RecentPanorama{year}
        adjacency_serializer = RecentAdjacency{year}Serializer
    """)


