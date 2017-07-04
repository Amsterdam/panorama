import datasets.panoramas.derived_models as models
import datasets.panoramas.derived_serializers as serializers
from . views import PanoramaViewSet


class RecentPanoramaViewSet(PanoramaViewSet):
    def list(self, request, *args, **kwargs):
        self._set_queryset_and_serializer(request)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
         self._set_queryset_and_detail_serializer(request)
         return super().retrieve(request, *args, **kwargs)

    def _set_queryset_and_serializer(self, request):
        self.recent_pano_model_class = models.getRecentPanoModel(request.path)
        self.queryset = self.recent_pano_model_class.done.all()
        self.serializer_class = serializers.getRecentPanoSerializer(
            self.recent_pano_model_class, request.path
        )

    def _set_queryset_and_detail_serializer(self, request):
        self._set_queryset_and_serializer(request)
        self.serializer_detail_class = serializers.getFilteredRecentPanoSerializer(
            self.recent_pano_model_class, request.path
        )

