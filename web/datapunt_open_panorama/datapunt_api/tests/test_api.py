# Python
import datetime
# Packages
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
            pano_id = 'PANO_1_2014',
            timestamp = factory.fuzzy.FuzzyDateTime(datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename = factory.fuzzy.FuzzyText(length=30),
            path = factory.fuzzy.FuzzyText(length=30),
            geolocation = Point(52.377956, 4.897070, 10),
            roll = factory.fuzzy.FuzzyFloat(-10, 10),
            pitch = factory.fuzzy.FuzzyFloat(-10, 10),
            heading = factory.fuzzy.FuzzyFloat(-10, 10),
        )
        factories.PanoramaFactory.create(
            pano_id = 'PANO_2_2014_CLOSE',
            timestamp = factory.fuzzy.FuzzyDateTime(datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename = factory.fuzzy.FuzzyText(length=30),
            path = factory.fuzzy.FuzzyText(length=30),
            geolocation = Point(52.377957, 4.897072, 12),
            roll = factory.fuzzy.FuzzyFloat(-10, 10),
            pitch = factory.fuzzy.FuzzyFloat(-10, 10),
            heading = factory.fuzzy.FuzzyFloat(-10, 10),
        )
        factories.PanoramaFactory.create(
            pano_id = 'PANO_3_2015_CLOSE',
            timestamp = factory.fuzzy.FuzzyDateTime(datetime.datetime(2015, 1, 1, tzinfo=UTC_TZ), force_year=2015),
            filename = factory.fuzzy.FuzzyText(length=30),
            path = factory.fuzzy.FuzzyText(length=30),
            geolocation = Point(52.377956, 4.897071, 10),
            roll = factory.fuzzy.FuzzyFloat(-10, 10),
            pitch = factory.fuzzy.FuzzyFloat(-10, 10),
            heading = factory.fuzzy.FuzzyFloat(-10, 10),
        )
        factories.PanoramaFactory.create(
            pano_id = 'PANO_4_2014_FAR',
            timestamp = factory.fuzzy.FuzzyDateTime(datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename = factory.fuzzy.FuzzyText(length=30),
            path = factory.fuzzy.FuzzyText(length=30),
            geolocation = Point(52.577956, 4.897170, 10),
            roll = factory.fuzzy.FuzzyFloat(-10, 10),
            pitch = factory.fuzzy.FuzzyFloat(-10, 10),
            heading = factory.fuzzy.FuzzyFloat(-10, 10),
        )

    # Tests
    #=============

    # Get by id
    def test_get_by_pano_id(self):
        response = self.client.get('/pano/PANO_1_2014/')
        # Making sure its a 200
        self.assertEqual(response.status_code, 200)
        # Malking sure data is correctly retrieved
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')
        # Testing 404 on non existing id
        response = self.client.get('/pano/PANO_NOT_DEFINED/')
        self.assertEqual(response.status_code, 404)

    def test_get_nearest_from_afar_no_radius(self):
        response = self.client.get('/pano/?lat=50&lon=4')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'],'PANO_1_2014')

    def test_get_nearest_from_afar_radius(self):
        response = self.client.get('/pano/?lat=50&lon=4&radius=10000')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('pano_id', response.data)

    def test_get_nearest_from_afar_no_radius_year(self):
        response = self.client.get('/pano/?lat=50&lon=4&vanaf=2015')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'],'PANO_3_2015_CLOSE')

    def test_get_nearest_close_no_radius(self):
        response = self.client.get('/pano/?lat=52.3779561&lon=4.8970701')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'],'PANO_1_2014')

    def test_get_nearest_close_radius(self):
        response = self.client.get('/pano/?lat=52.3779561&lon=4.8970701&radius=1000')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'],'PANO_1_2014')

    def test_get_nearest_close_no_radius_max_date(self):
        response = self.client.get('/pano/?lat=52.3779561&lon=4.8970701&tot=01-01-2015')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'],'PANO_1_2014')

    def test_get_nearest_all_parameters(self):
        response = self.client.get('/pano/?lat=52.377958&lon=4.897070&radius=10000&vanaf=2014-01-01&tot=2016')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'],'PANO_1_2014')
