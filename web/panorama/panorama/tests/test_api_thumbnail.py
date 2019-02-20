# Python
import datetime
# Packages
from django.contrib.gis.geos import Point
from django.utils.timezone import utc as UTC_TZ
import factory
import factory.fuzzy
# Project
from . test_api_base import PanoramaApiTest
from datasets.panoramas.v1.models import Panorama
from datasets.panoramas.tests import factories

class ThumbnailApiTest(PanoramaApiTest):

    def test_get_thumbnail_returns_json(self):
        response = self.client.get(
            '/panorama/thumbnail/?lat=52.377956&lon=4.897070&radius=100')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertIn('url', response.data)
        self.assertIn('heading', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_9_2017_CLOSE_BUT_NO_CIGAR')
        self.assertEqual(response.data['url'], 'http://testserver/panorama/thumbnail/PANO_9_2017_CLOSE_BUT_NO_CIGAR/?heading=270')
        self.assertEqual(response.data['heading'], 270)

    def test_get_thumbnail_returns_jpg(self):
        response = self.client.get('/panorama/thumbnail/?lat=52.377956&lon=4.897070&radius=1000',
                                   follow=False,
                                   HTTP_ACCEPT='image/jpeg')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/panorama/thumbnail/PANO_9_2017_CLOSE_BUT_NO_CIGAR/?heading=270')

    def test_get_thumbnail_returns_json_with_qparams(self):
        response = self.client.get('/panorama/thumbnail/?lat=52.377956&lon=4.897070&radius=1000&width=600',
                                   follow=False,
                                   HTTP_ACCEPT='image/jpeg')
        self.assertEqual(response.status_code, 302)
        self.assertIn('http://testserver/panorama/thumbnail/PANO_9_2017_CLOSE_BUT_NO_CIGAR/?', response['Location'])
        self.assertIn('heading=270', response['Location'])
        self.assertIn('width=600', response['Location'])
