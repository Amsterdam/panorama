import factory

from .. import models


class PanoramaFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Panorama


class TrajectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Traject
