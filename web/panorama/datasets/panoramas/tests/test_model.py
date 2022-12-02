from unittest import TestCase

from django.contrib.gis.geos import Point
from django.conf import settings

from datasets.panoramas.models import Panoramas


class TestModel(TestCase):

    def test_img_url(self):
        cases = [
            ('container/path/',
             'image.jpg',
             settings.PANO_IMAGE_URL + '/container/path/image/equirectangular/panorama_8000.jpg',
             settings.PANO_IMAGE_URL + '/container/path/image/equirectangular/panorama_4000.jpg',
             settings.PANO_IMAGE_URL + '/container/path/image/equirectangular/panorama_2000.jpg',
             settings.PANO_IMAGE_URL + '/container/path/image/cubic/',
             settings.PANO_IMAGE_URL + '/container/path/image/cubic/{z}/{f}/{y}/{x}.jpg',
             settings.PANO_IMAGE_URL + '/container/path/image/cubic/preview.jpg'),
        ]
        for c in cases:
            p = Panoramas(path=c[0], filename=c[1], geolocation=Point(1, 1, 1))
            self.assertEqual(c[2], p.equirectangular_full)
            self.assertEqual(c[3], p.equirectangular_medium)
            self.assertEqual(c[4], p.equirectangular_small)
            self.assertEqual(c[5], p.cubic_img_baseurl)
            self.assertEqual(c[6], p.cubic_img_pattern)
            self.assertEqual(c[7], p.cubic_img_preview)

    def get_raw_image_objectstore_id(self):
        cases = [
            ('container/path/', 'image.jpg', {'container': 'container', 'name': 'path/image.jpg'}),
        ]

        for c in cases:
            p = Panoramas(path=c[0], filename=c[1], geolocation=Point(1, 1, 1))
            self.assertEqual(c[2], p.get_raw_image_objectstore_id())
