import logging
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
