from django.contrib.gis.db import models as geo
from django.db import models
# Project
from datapunt_open_panorama.settings import PANO_DIR, PANO_IMAGE_URL


class Panorama(models.Model):
    id = models.AutoField(primary_key=True)
    pano_id = models.CharField(max_length=37, unique=True)
    timestamp = models.DateTimeField()
    filename = models.CharField(max_length=255)
    path = models.CharField(max_length=400)
    geolocation = geo.PointField(dim=3, srid=4326, spatial_index=True)
    roll = models.FloatField()
    pitch = models.FloatField()
    heading = models.FloatField()

    objects = geo.GeoManager()

    def __str__(self):
        return '<Panorama %s/%s>' % (self.path, self.filename)

    @property
    def img_url(self):
        return '%s%s/%s' %(PANO_IMAGE_URL, self.path.replace(PANO_DIR, ''), self.filename)


class Traject(models.Model):
    timestamp = models.DateTimeField()
    geolocation = geo.PointField(dim=3)
    north_rms = models.DecimalField(
        max_digits=20, decimal_places=14)
    east_rms = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=14)
    down_rms = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=14)
    roll_rms = models.FloatField(null=True, blank=True)
    pitch_rms = models.FloatField(null=True, blank=True)
    heading_rms = models.FloatField(null=True, blank=True)

    objects = geo.GeoManager()

    def __str__(self):
        return '<Traject %d>' % self.pk
