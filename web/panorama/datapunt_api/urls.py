# Packages
from django.conf import settings
from django.conf.urls import url, include
from rest_framework import renderers
from rest_framework import response
from rest_framework import routers
from rest_framework import schemas
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_swagger.renderers import OpenAPIRenderer
from rest_framework_swagger.renderers import SwaggerUIRenderer

from .view_imgs import ThumbnailViewSet
from .views import PanoramaViewSet


class PanoramaRouter(routers.DefaultRouter):
    """
    Panoramabeelden Amsterdam

    Deze api geeft toegang tot de panorama beelden van de Gemeente Amsterdam en omstreken.
    """

    def get_api_root_view(self, **kwargs):
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class Panoramabeelden(cls):
            pass

        Panoramabeelden.__doc__ = self.__doc__
        return Panoramabeelden.as_view()


panorama = PanoramaRouter()
panorama.register(r'opnamelocatie', PanoramaViewSet, base_name='panorama')
panorama.register(r'thumbnail', ThumbnailViewSet, base_name='thumbnail')

APIS = [
    url(r'^panorama/', include(panorama.urls))
]


@api_view()
@renderer_classes(
    [SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def swagger_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='Panoramabeelden Amsterdam API', urlpatterns=APIS)
    return response.Response(
        generator.get_schema(request=request)
    )


urlpatterns = APIS + [
    url(r'^status/', include('health.urls')),
    url('^panorama/docs/$', swagger_schema_view),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
