from django.conf.urls import url, include
from rest_framework import routers


class PanoramaView(routers.APIRootView):
    """
    De panoramas van de stad worden in een lijst getoond

    - panorama's
    - thumbnails
    - recente panorama's
    """


class PanoramaRouter(routers.DefaultRouter):
    """
    Panoramabeelden Amsterdam

    Deze api geeft toegang tot de panorama beelden van de Gemeente Amsterdam en omstreken.
    """

    APIRootView = PanoramaView


panorama = PanoramaRouter()

urlpatterns = [url(r"^panorama/", include(panorama.urls))]
