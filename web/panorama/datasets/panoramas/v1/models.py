from django.db import models
from django.db.models import Manager

from datasets.panoramas.models import AbstractBasePanorama


class AbstractPanorama(AbstractBasePanorama):
    objects = Manager()

    roll = models.FloatField()
    pitch = models.FloatField()
    heading = models.FloatField()

    class Meta(AbstractBasePanorama.Meta):
        abstract = True

    @property
    def cubic_img_urls(self):
        return {'baseurl': self.cubic_img_baseurl,
                'pattern': self.cubic_img_pattern,
                'preview': self.cubic_img_preview}

    @property
    def equirectangular_img_urls(self):
        return {'full': self.equirectangular_full,
                'medium': self.equirectangular_medium,
                'small': self.equirectangular_small}


class Panorama(AbstractPanorama):
    class Meta(AbstractPanorama.Meta):
        abstract = False


class RecentPanorama(AbstractPanorama):
    class Meta(AbstractPanorama.Meta):
        abstract = False
        managed = False
        db_table = "panoramas_recent_all"
