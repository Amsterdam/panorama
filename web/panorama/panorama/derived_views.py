from datasets.panoramas.derived_models import RecentPanorama
from datasets.panoramas.derived_serializers import RecentPanoSerializer, FilteredRecentPanoSerializer

from . views import PanoramaViewSet


class RecentPanoramaViewSet(PanoramaViewSet):
    queryset = RecentPanorama.done.all()
    serializer_detail_class = FilteredRecentPanoSerializer
    serializer_class = RecentPanoSerializer

    def get_object(self):
        return super().get_object()
