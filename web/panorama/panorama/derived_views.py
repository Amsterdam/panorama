import datasets.panoramas.derived_models as models
import datasets.panoramas.derived_serializers as serializers
from . views import PanoramaViewSet


class RecentPanoramaViewSet(PanoramaViewSet):
    def list(self, request, *args, **kwargs):
        self._set_queryset_and_serializers(request.path)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self._set_queryset_and_serializers(request.path)
        return super().retrieve(request, *args, **kwargs)

    def _set_queryset_and_serializers(self, path):
        recent_pano_model_class = models.getRecentPanoModel(path)
        self.queryset = recent_pano_model_class.done.all()
        self.serializer_class = serializers.getRecentPanoSerializer(
            recent_pano_model_class, path)
        self.serializer_detail_class = serializers.getFilteredRecentPanoSerializer(
            recent_pano_model_class, path)
