# Packages
from django.conf.urls import url, include
from rest_framework import routers
# Project
from .views import PanoViewSet
from health import views


class DocumentedRouter(routers.DefaultRouter):
    """
    """

    def get_api_root_view(self):
        view = super().get_api_root_view()
        cls = view.cls

        class Datapunt(cls):
            pass

        Datapunt.__doc__ = self.__doc__
        return Datapunt.as_view()


# router = DocumentedRouter()
router = routers.DefaultRouter()

# Registering the API endpoints
router.register(r'panorama', PanoViewSet)


urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls)),
    url(r'^status/health$', views.health),
]
