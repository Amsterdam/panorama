from math import atan2, degrees, cos, sin, radians

from django.contrib.gis.db import models as geo
from django.contrib.gis.geos import Point
from django.db import models
from django.conf import settings

from model_utils.models import StatusModel
from model_utils import Choices

# Project

CUBIC_SUBPATH = '/cubic/'
EQUIRECTANGULAR_SUBPATH = '/equirectangular/'

SMALL_IMAGE_NAME = 'panorama_2000.jpg'
MEDIUM_IMAGE_NAME = 'panorama_4000.jpg'
FULL_IMAGE_NAME = 'panorama_8000.jpg'

MARZIPANO_URL_PATTERN = '{z}/{f}/{y}/{x}.jpg'
PREVIEW_IMAGE = 'preview.jpg'

MISSION_TYPE_CHOICES = (
    ('L', 'land'),
    ('W', 'water'),
)


class AbstractPanoramaNew(StatusModel):
    STATUS = Choices(
        'to_be_rendered', 'rendering', 'rendered', 'detecting_regions', 'detected', 'blurring', 'done')

    id = models.AutoField(primary_key=True)
    pano_id = models.CharField(max_length=37, unique=True, db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    filename = models.CharField(max_length=255)
    path = models.CharField(max_length=400)
    geolocation = geo.PointField(dim=3, srid=4326, spatial_index=True)
    _geolocation_2d = geo.PointField(dim=2, srid=4326, spatial_index=True, null=True)
    _geolocation_2d_rd = geo.PointField(dim=2, srid=28992, spatial_index=True, null=True)
    roll = models.FloatField()
    pitch = models.FloatField()
    heading = models.FloatField()

    mission_type = models.CharField(
        max_length=1, choices=MISSION_TYPE_CHOICES, default='L')

    objects = geo.GeoManager()

    class Meta:
        ordering = ('id',)
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self._geolocation_2d or not self._geolocation_2d_rd:
            self._derive_calculated_fields()

    def _derive_calculated_fields(self):
        point = Point(self.geolocation[0], self.geolocation[1], srid=4326)
        self._geolocation_2d = point
        self._geolocation_2d_rd = point.transform(28992, clone=True)

    def save(self, *args, **kwargs):
        self._derive_calculated_fields()
        super().save(*args, **kwargs)

    def __str__(self):
        return '<Panorama %s%s>' % (self.path, self.filename)

    def get_raw_image_objectstore_id(self):
        container = self.path.split('/')[0]
        name = (self.path+self.filename).replace(container+'/', '')
        return {'container': container, 'name': name}

    def get_intermediate_url(self):
        objectstore_id = self.get_raw_image_objectstore_id()
        return f"{objectstore_id['container']}/{objectstore_id['name']}"

    @property
    def cubic_img_urls(self):

        baseurl = '{}/{}{}'.format(
            settings.PANO_IMAGE_URL, self.path,
            self.filename[:-4] + CUBIC_SUBPATH)

        return {'baseurl': baseurl,
                'pattern': baseurl + MARZIPANO_URL_PATTERN,
                'preview': baseurl + PREVIEW_IMAGE}

    @property
    def detection_result_dir(self):
        return 'results/{}{}'.format(self.path, self.filename[:-4])

    @property
    def equirectangular_img_urls(self):
        baseurl = '{}/{}{}'.format(
            settings.PANO_IMAGE_URL,
            self.path,
            self.filename[:-4] + EQUIRECTANGULAR_SUBPATH)

        return {'full': baseurl + FULL_IMAGE_NAME,
                'medium': baseurl + MEDIUM_IMAGE_NAME,
                'small': baseurl + SMALL_IMAGE_NAME}


class PanoramaNew(AbstractPanoramaNew):
    class Meta(AbstractPanoramaNew.Meta):
        abstract = False
        managed = False
        db_table = 'panoramas_panorama'


class AbstractAdjacencyNew(models.Model):
    to_pano_id = models.CharField(max_length=37)
    from_pano_id = models.CharField(max_length=37)

    to_year = models.IntegerField()

    heading = models.DecimalField(max_digits=20, decimal_places=2)
    distance = models.DecimalField(max_digits=20, decimal_places=2)
    direction = models.DecimalField(max_digits=20, decimal_places=2)
    angle = models.DecimalField(max_digits=20, decimal_places=2)
    pitch = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        abstract = True
        managed = False

    def __str__(self):
        return '<Adjacency %s -> /%s>' % (self.from_pano_id, self.to_pano_id)


class AdjacencyNew(AbstractAdjacencyNew):
    class Meta(AbstractAdjacencyNew.Meta):
        abstract = False
        db_table = "adjacencies_new"


class RegionNew(models.Model):
    REGION_TYPES = (
        ('N', 'Nummerbord'),
        ('G', 'Gezicht')
    )
    id = models.AutoField(primary_key=True)
    pano_id = models.CharField(max_length=37, default='', db_index=True)
    region_type = models.CharField(max_length=1, choices=REGION_TYPES)
    detected_by = models.CharField(max_length=255)

    # coordinates from left top, clockwise
    left_top_x = models.IntegerField()
    left_top_y = models.IntegerField()
    right_top_x = models.IntegerField()
    right_top_y = models.IntegerField()
    right_bottom_x = models.IntegerField()
    right_bottom_y = models.IntegerField()
    left_bottom_x = models.IntegerField()
    left_bottom_y = models.IntegerField()

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f"<Region {self.id} of Panorama {self.panorama.pano_id}>"


class TrajectNew(models.Model):
    timestamp = models.DateTimeField()
    geolocation = geo.PointField(dim=3, spatial_index=True)
    north_rms = models.DecimalField(
        max_digits=20, decimal_places=14)
    east_rms = models.DecimalField(
        null=True, blank=True, max_digits=20, decimal_places=14)
    down_rms = models.DecimalField(
        null=True, blank=True, max_digits=20, decimal_places=14)
    roll_rms = models.FloatField(null=True, blank=True)
    pitch_rms = models.FloatField(null=True, blank=True)
    heading_rms = models.FloatField(null=True, blank=True)

    objects = geo.GeoManager()

    def __str__(self):
        return '<Traject %d>' % self.pk


class MissionNew(models.Model):
    def __str__(self):
        return f"<Mission {self.name} {self.type} - {self.neighbourhood}>"

    name = models.TextField(max_length=24, unique=True)
    type = models.CharField(max_length=1, choices=MISSION_TYPE_CHOICES)
    date = models.DateField()
    neighbourhood = models.TextField(max_length=50)
