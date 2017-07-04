import logging
from collections import OrderedDict

from datasets.panoramas import derived_models as models
from . serializers import AdjacencySerializer, PanoSerializer, FilteredPanoSerializer, PanoLinksField

log = logging.getLogger(__name__)


def getRecentPanoSerializer(recent_pano_model, path):
    class RecentPanoSerializer(PanoSerializer):
        serializer_url_field = getPanoLinksField(path)
        class Meta(PanoSerializer.Meta):
            model = recent_pano_model

    return RecentPanoSerializer


def getRecentAdjacencySerializer(recent_pano_model):
    class RecentAdjacencySerializer(AdjacencySerializer):
        class Meta(AdjacencySerializer.Meta):
            model = recent_pano_model

    return RecentAdjacencySerializer


def getFilteredRecentPanoSerializer(recent_pano_model, path):
    class FilteredRecentPanoSerializer(FilteredPanoSerializer):
        serializer_url_field = getPanoLinksField(path)
        class Meta(PanoSerializer.Meta):
            model = recent_pano_model

        class Models(FilteredPanoSerializer.Models):
            adjacency_model = models.getRecentAdjacencyModel(recent_pano_model, path)
            adjacency_serializer = getRecentAdjacencySerializer(recent_pano_model)

    return FilteredRecentPanoSerializer


def getPanoLinksField(path):
    index_of_set = path.index('recente_opnames/') + len('recente_opnames/')
    set = path[index_of_set:index_of_set+4]

    class RecentPanoLinksField(PanoLinksField):
        def to_representation(self, value):
            request = self.context.get('request')
            modified_view_name = self.view_name.replace('recentpanorama', f"recentpanorama-{set}")
            return OrderedDict([
                ('self', dict(href=self.get_url(value, modified_view_name, request, None))),
            ])

    return RecentPanoLinksField