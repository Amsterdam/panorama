import factory

import datasets.panoramas.v1.models
from .. import models


class PanoramaFactory(factory.DjangoModelFactory):
    class Meta:
        model = datasets.panoramas.v1.models.Panorama


class TrajectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Traject

