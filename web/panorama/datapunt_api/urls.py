# Packages
from django.conf.urls import url, include
from rest_framework import routers
# Project
from .views import PanoramaViewSet
from .view_imgs import ThumbnailViewSet


class PanoramaRouter(routers.DefaultRouter):
    """
    Panorama's van Amsterdam
    """

    def get_api_root_view(self):
        view = super().get_api_root_view()
        cls = view.cls

        class Panorama(cls):
            pass

        Panorama.__doc__ = self.__doc__
        return Panorama.as_view()


panorama = routers.DefaultRouter()
panorama.register(r'opnamelocatie', PanoramaViewSet, base_name='panorama')
panorama.register(r'thumbnail', ThumbnailViewSet, base_name='thumbnail')

urlpatterns = [
    url(r'^panorama/', include(panorama.urls)),
    url(r'^status/', include('health.urls')),
]
