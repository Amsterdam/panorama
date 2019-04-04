import factory

from .. import models


class PanoramaFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Panoramas


class TrajectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Traject

