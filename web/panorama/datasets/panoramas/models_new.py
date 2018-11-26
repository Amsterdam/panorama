from django.contrib.gis.db import models as geo
from django.db.models import Manager
from django.contrib.gis.geos import Point
from django.db import models
from django.conf import settings
from django.urls import reverse

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


class Panoramas(StatusModel):

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

    surface_type = models.CharField(max_length=1, choices=SURFACE_TYPE_CHOICES, default='L')
    mission_distance = models.IntegerField()
    mission_type = models.TextField(max_length=16, default='bi')
    mission_year = models.TextField(max_length=4, null=True)

    objects = Manager()

    class Meta:
        managed = False
        db_table = 'panoramas_panorama'
        ordering = ('id',)

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
    def detection_result_dir(self):
        return 'results/{}{}'.format(self.path, self.filename[:-4])

    @property
    def thumbnail(self):
        return reverse('thumbnail-detail', args=(self.pano_id,))

    @property
    def adjacencies(self):
        return reverse('panoramas-adjacencies', args=(self.pano_id,))

    @property
    def img_baseurl(self):
        return f"{settings.PANO_IMAGE_URL}/{self.path}{self.filename[:-4]}"

    @property
    def cubic_img_baseurl(self):
        return self.img_baseurl + CUBIC_SUBPATH

    @property
    def cubic_img_pattern(self):
        return self.cubic_img_baseurl + MARZIPANO_URL_PATTERN

    @property
    def cubic_img_preview(self):
        return self.cubic_img_baseurl + PREVIEW_IMAGE

    @property
    def equirectangular_full(self):
        return self.img_baseurl + EQUIRECTANGULAR_SUBPATH + FULL_IMAGE_NAME

    @property
    def equirectangular_medium(self):
        return self.img_baseurl + EQUIRECTANGULAR_SUBPATH + MEDIUM_IMAGE_NAME

    @property
    def equirectangular_small(self):
        return self.img_baseurl + EQUIRECTANGULAR_SUBPATH + SMALL_IMAGE_NAME


class Adjacencies(Panoramas):
    from_pano_id = models.CharField(max_length=37)
    from_geolocation_2d_rd = geo.PointField(dim=2, srid=28992, spatial_index=True)

    relative_distance = models.FloatField()
    relative_pitch = models.FloatField()
    relative_heading = models.FloatField()

    class Meta(Panoramas.Meta):
        db_table = "panoramas_adjacencies_new"

    def __str__(self):
        return '<Adjacency %s -> /%s>' % (self.from_pano_id, self.pano_id)
