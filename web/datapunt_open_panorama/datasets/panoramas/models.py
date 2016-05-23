from django.db import models
from django.contrib.gis.db import models as geo


class Panorama(models.Model):
    timestamp = models.TimeField(null=True)
    filename = models.CharField(null=True, max_length=255)
    opnamelocatie = geo.PointField(null=True, dim=3)
    roll = models.FloatField(null=True)
    pitch = models.FloatField(null=True)
    heading = models.FloatField(null=True)

    objects = geo.GeoManager()

    def __str__(self):
        return '<Panorama %s>' % self.filename


class Traject(models.Model):
    timestamp = models.TimeField(null=True)
    opnamelocatie = geo.PointField(null=True, dim=3)
    north_rms = models.DecimalField(null=True, max_digits=20, decimal_places=14)
    east_rms = models.DecimalField(null=True, max_digits=20, decimal_places=14)
    down_rms = models.DecimalField(null=True, max_digits=20, decimal_places=14)
    roll_rms = models.FloatField(null=True)
    pitch_rms = models.FloatField(null=True)
    heading_rms = models.FloatField(null=True)

    objects = geo.GeoManager()

    def __str__(self):
        return '<Traject %d>' % self.pk
