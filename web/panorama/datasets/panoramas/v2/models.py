from django.contrib.gis.db import models as geo
from django.db import models
from django.urls import reverse


# Project
from datasets.panoramas.models import AbstractBasePanorama


class AbstractPanoramas(AbstractBasePanorama):
    @property
    def thumbnail(self):
        return reverse('thumbnail-detail', args=(self.pano_id,))

    @property
    def adjacencies(self):
        return reverse('panoramas-adjacencies', args=(self.pano_id,))


class Panoramas(AbstractPanoramas):
    class Meta(AbstractPanoramas.Meta):
        abstract = False
        managed = False
        db_table = 'panoramas_panorama'


class Adjacencies(AbstractPanoramas):
    from_pano_id = models.CharField(max_length=37)
    from_geolocation_2d_rd = geo.PointField(dim=2, srid=28992, spatial_index=True)

    relative_distance = models.FloatField()
    relative_pitch = models.FloatField()
    relative_heading = models.FloatField()
    relative_elevation = models.FloatField()

    class Meta(AbstractPanoramas.Meta):
        abstract = False
        managed = False
        db_table = "panoramas_adjacencies_new"

    def __str__(self):
        return '<Adjacency %s -> /%s>' % (self.from_pano_id, self.pano_id)
