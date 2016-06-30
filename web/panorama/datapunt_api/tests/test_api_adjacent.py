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
from datapunt.management.commands import refresh_views


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
            geolocation=Point(4.94444897029152, 52.3510468066549, 10),
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
            geolocation=Point(4.94439711277457, 52.3510810574283, 12),
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
            geolocation=Point(4.94439711277457, 52.3510810574283, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
        )
        refresh = refresh_views.Command()
        refresh.refresh_views()

    # Tests
    # =============

    def test_get_base_panorama(self):
        response = self.client.get('/panorama/opnamelocatie/PANO_1_2014/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')
        self.assertIn('adjacent', response.data)
        self.assertEqual(2, len(response.data['adjacent']))
        self.assertIn('pano_id', response.data['adjacent'][0])
        self.assertIn('angle', response.data['adjacent'][0])
        self.assertIn('direction', response.data['adjacent'][0])

    def test_filtering_on_date1(self):
        response = self.client.get('/panorama/opnamelocatie/?lat=52.3510468066549&lon=4.94444897029152&tot=2015-01-01')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')
        self.assertIn('adjacent', response.data)
        self.assertEqual(1, len(response.data['adjacent']))
        self.assertIn('pano_id', response.data['adjacent'][0])
        self.assertEqual(response.data['adjacent'][0]['pano_id'], 'PANO_2_2014_CLOSE')

    def test_filtering_on_date2(self):
        response = self.client.get('/panorama/opnamelocatie/?lat=52.3510468066549&lon=4.94444897029152&vanaf=2015-01-01')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_3_2015_CLOSE')
        self.assertIn('adjacent', response.data)
        self.assertFalse(response.data['adjacent'])
