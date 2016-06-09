from django.db import models
from django.contrib.gis.db import models as geo


class Panorama(models.Model):
    id = models.AutoField(primary_key=True)
    pano_id = models.CharField(max_length=37, unique=True)
    timestamp = models.DateTimeField()
    filename = models.CharField(max_length=255)
    path = models.CharField(max_length=400)
    opnamelocatie = geo.PointField(dim=3)
    roll = models.FloatField()
    pitch = models.FloatField()
    heading = models.FloatField()

    objects = geo.GeoManager()

    def __str__(self):
        return '<Panorama %s/%s>' % (self.path, self.filename)


class Traject(models.Model):
    timestamp = models.DateTimeField()
    opnamelocatie = geo.PointField(dim=3)
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
