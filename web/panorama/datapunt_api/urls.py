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
    PANORAMAS

    Deze api geeft toegang tot de panorama beelden van de Gemeente Amsterdam en omstreken.
    """

    def get_api_root_view(self, **kwargs):
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class Panorama(cls):
            pass

        Panorama.__doc__ = self.__doc__
        return Panorama.as_view()


panorama = routers.DefaultRouter()
panorama.register(r'opnamelocatie', PanoramaViewSet, base_name='panorama')
panorama.register(r'thumbnail', ThumbnailViewSet, base_name='thumbnail')


@api_view()
@renderer_classes(
    [SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def swagger_schema_view(request):
    generator = schemas.SchemaGenerator(title='Panoramas API')
    return response.Response(generator.get_schema(request=request))


urlpatterns = [
    url(r'^panorama/', include(panorama.urls)),
    url(r'^status/', include('health.urls')),
    url('^panorama/docs/$', swagger_schema_view),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
