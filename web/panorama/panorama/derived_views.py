from datasets.panoramas.derived_models import *
from datasets.panoramas.derived_serializers import *
from django.conf import settings

from . views import PanoramaViewSet


class RecentPanoramaViewSet(PanoramaViewSet):
    queryset = RecentPanorama.done.all()
    serializer_detail_class = FilteredRecentPanoSerializer
    serializer_class = RecentPanoSerializer


for year in settings.PREPARED_YEARS:
    exec(f"""
class RecentPanorama{year}ViewSet(PanoramaViewSet):
    queryset = RecentPanorama{year}.done.all()
    serializer_detail_class = FilteredRecentPano{year}Serializer
    serializer_class = RecentPano{year}Serializer
    """)
