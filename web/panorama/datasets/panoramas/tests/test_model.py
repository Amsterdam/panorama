from unittest import TestCase

from django.contrib.gis.geos import Point

from .. import models


class TestModel(TestCase):

    def test_img_url(self):
        cases = [
            ('container/path', 'image.jpg', 'https://acc.atlas.amsterdam.nl/panorama/container/path/image_normalized.jpg'),
        ]
        for c in cases:
            p = models.Panorama(path=c[0], filename=c[1], geolocation=Point(1,1,1))
            self.assertEqual(c[2], p.img_url)

    def get_raw_image_objectstore_id(self):
        cases = [
            ('container/path/', 'image.jpg', {'container':'container', 'name': 'path/image.jpg'}),
        ]

        for c in cases:
            p = models.Panorama(path=c[0], filename=c[1], geolocation=Point(1,1,1))
            self.assertEqual(c[2], p.get_raw_image_objectstore_id())
