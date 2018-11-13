from math import atan2, degrees, cos, sin, radians

from django.contrib.gis.db import models as geo
from django.db.models import Manager
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

SURFACE_TYPE_CHOICES = (
    ('L', 'land'),
    ('W', 'water'),
)


class AbstractPanorama(StatusModel):
    STATUS = Choices(
        'to_be_rendered', 'rendering', 'rendered', 'detecting_regions', 'detected', 'blurring', 'done')

    id = models.AutoField(primary_key=True)
    pano_id = models.CharField(max_length=37, unique=True, db_index=True)
    timestamp = models.DateTimeField()
    filename = models.CharField(max_length=255)
    path = models.CharField(max_length=400)
    geolocation = geo.PointField(dim=3, srid=4326, spatial_index=True)
    _geolocation_2d = geo.PointField(dim=2, srid=4326, spatial_index=True, null=True)
    _geolocation_2d_rd = geo.PointField(dim=2, srid=28992, spatial_index=True, null=True)
    roll = models.FloatField()
    pitch = models.FloatField()
    heading = models.FloatField()
    adjacent_panos = models.ManyToManyField(
        'self', through='Adjacency', symmetrical=False)
    surface_type = models.CharField(max_length=1, choices=SURFACE_TYPE_CHOICES, default='L')
    mission_type = models.TextField(max_length=16, default='bi')
    mission_year = models.TextField(max_length=4, null=True)

    objects = Manager()

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


class Panorama(AbstractPanorama):
    class Meta(AbstractPanorama.Meta):
        abstract = False


class AbstractAdjacency(models.Model):
    from_pano = models.ForeignKey(Panorama, on_delete=models.CASCADE, related_name='to_adjacency')
    to_pano = models.ForeignKey(Panorama, on_delete=models.CASCADE, related_name='from_adjacency')
    heading = models.DecimalField(max_digits=20, decimal_places=2)
    to_year = models.IntegerField()
    distance = models.FloatField()
    elevation = models.FloatField()

    class Meta:
        abstract = True
        index_together = [['from_pano', 'distance']]
        managed = False

    def __str__(self):
        return '<Adjacency %s -> /%s>' % (self.from_pano_id, self.to_pano_id)

    @property
    def direction(self):
        return (self.heading - self.from_pano.heading) % 360

    @property
    def angle(self):
        cam_angle = self.from_pano.pitch*cos(radians(self.direction)) \
                    - self.from_pano.roll*sin(radians(self.direction))
        return self.pitch - cam_angle

    @property
    def pitch(self):
        if not self.elevation or self.distance <= 0.0:
            return 0.0
        return degrees(atan2(self.elevation, self.distance))


class Adjacency(AbstractAdjacency):
    class Meta(AbstractAdjacency.Meta):
        abstract = False
        db_table = "panoramas_adjacencies"


class Region(models.Model):
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


class Traject(models.Model):
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

    objects = Manager()

    def __str__(self):
        return '<Traject %d>' % self.pk


class Mission(models.Model):
    def __str__(self):
        return f"<Mission {self.name} {self.type} - {self.neighbourhood}>"

    name = models.TextField(max_length=24, unique=True)
    neighbourhood = models.TextField(max_length=50,null=True)
    surface_type = models.CharField(max_length=1, choices=SURFACE_TYPE_CHOICES, default='L')
    mission_type = models.TextField(max_length=16, default='bi')
    mission_year = models.TextField(max_length=4, null=True)
    date = models.DateField(null=True)
