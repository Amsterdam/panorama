# Python
import datetime
from unittest.mock import Mock
# Packages
from django.http import HttpResponse
from corsheaders.middleware import CorsMiddleware
from django.contrib.gis.geos import Point
from django.utils.timezone import utc as UTC_TZ
import factory
import factory.fuzzy
from rest_framework.test import APITestCase
# Project
from datasets.panoramas.tests import factories


class PanoramaApiTest(APITestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        # Adding locations
        factories.PanoramaFactory.create(
            pano_id='PANO_1_2014',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.897070, 52.377956, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_2_2014_CLOSE',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.897072, 52.377957, 12),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_3_2015_CLOSE',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2015, 1, 1, tzinfo=UTC_TZ), force_year=2015),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.897071, 52.377956, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_4_2014_FAR',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.897170, 52.577956, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
        )

    # Tests
    # =============

    # Get by id
    def test_get_by_pano_id(self):
        response = self.client.get('/panorama/opnamelocatie/PANO_1_2014/')
        # Making sure its a 200
        self.assertEqual(response.status_code, 200)
        # Malking sure data is correctly retrieved
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')
        # Testing 404 on non existing id
        response = self.client.get('/panorama/opnamelocatie/PANO_NOT_DEFINED/')
        self.assertEqual(response.status_code, 404)

    def test_get_nearest_from_afar_no_radius(self):
        response = self.client.get('/panorama/opnamelocatie/?lat=50&lon=4')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('pano_id', response.data)

    def test_get_nearest_from_afar_radius(self):
        response = self.client.get('/panorama/opnamelocatie/?lat=50&lon=4&radius=10000')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('pano_id', response.data)

    def test_get_nearest_from_afar_no_radius_year(self):
        response = self.client.get('/panorama/opnamelocatie/?lat=50&lon=4&vanaf=2015')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('pano_id', response.data)

    def test_fieldset_to_spec(self):
        response = self.client.get('/panorama/opnamelocatie/?lat=52.37795&lon=4.8970')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertIn('geometrie', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')
        self.assertNotIn('path', response.data)
        self.assertNotIn('geolocation', response.data)

    def test_get_nearest_close_no_radius(self):
        response = self.client.get('/panorama/opnamelocatie/?lat=52.37795&lon=4.8970')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')

    def test_get_nearest_close_no_radius_but_too_far(self):
        response = self.client.get('/panorama/opnamelocatie/?lat=52.377&lon=4.8970')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('pano_id', response.data)

    def test_get_nearest_close_radius(self):
        response = self.client.get(
            '/panorama/opnamelocatie/?lat=52.3779561&lon=4.8970701&radius=1000')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')

    def test_get_nearest_close_no_radius_max_date(self):
        response = self.client.get(
            '/panorama/opnamelocatie/?lat=52.3779561&lon=4.8970701&tot=01-01-2015')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')

    def test_get_nearest_all_parameters(self):
        response = self.client.get(
            '/panorama/opnamelocatie/?lat=52.377958&lon=4.897070&radius=10000&vanaf=2014-01-01&tot=2016')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')

    def test_get_status_health(self):
        """
            Tests both the pass of database-cursor as well as the missing of db-content
        """
        response=self.client.get('/status/health')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Too few Panoramas', str(response.content))

    def test_get_thumbnail_returns_json(self):
        response = self.client.get(
            '/panorama/thumbnail/?lat=52.3779561&lon=4.8970701&radius=1000')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertIn('url', response.data)
        self.assertIn('heading', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')
        self.assertEqual(response.data['url'], 'http://testserver/panorama/thumbnail/PANO_1_2014/?heading=31')
        self.assertEqual(response.data['heading'], 31)

    def test_get_thumbnail_returns_jpg(self):
        response = self.client.get('/panorama/thumbnail/?lat=52.3779561&lon=4.8970701&radius=1000',
                                    follow=False,
                                    HTTP_ACCEPT='image/jpeg')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/panorama/thumbnail/PANO_1_2014/?heading=31')

    def test_get_thumbnail_returns_json_with_qparams(self):
        response = self.client.get('/panorama/thumbnail/?lat=52.3779561&lon=4.8970701&radius=1000&width=600',
                                   follow=False,
                                   HTTP_ACCEPT='image/jpeg')
        self.assertEqual(response.status_code, 302)
        self.assertIn('http://testserver/panorama/thumbnail/PANO_1_2014/?', response['Location'])
        self.assertIn('heading=31', response['Location'])
        self.assertIn('width=600', response['Location'])

    def test_cors(self):
        """
        Cross Origin Requests should be allowed.
        """
        request = Mock(path='https://api.datapunt.amsterdam.nl/panorama/opnamelocatie/?lat=52.3779561&lon=4.8970701')
        request.method = 'GET'
        request.is_secure = lambda: True
        request.META = {
            'HTTP_REFERER': 'https://foo.google.com',
            'HTTP_HOST': 'api.datapunt.amsterdam.nl',
            'HTTP_ORIGIN': 'https://foo.google.com',
        }
        response = CorsMiddleware().process_response(request, HttpResponse())
        self.assertTrue('access-control-allow-origin' in response._headers)
        self.assertEquals(
            '*', response._headers['access-control-allow-origin'][1])
