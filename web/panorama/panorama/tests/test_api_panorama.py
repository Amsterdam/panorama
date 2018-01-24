# Project
from . test_api_base import PanoramaApiTest


class OpnameLocatieApiTest(PanoramaApiTest):
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
        response = self.client.get('/panorama/opnamelocatie/PANO_1_2014/')
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
        self.assertEqual(response.data['pano_id'], 'PANO_7_2016_CLOSE_BUT_NO_CIGAR')

    def test_get_nearest_close_no_radius_but_too_far(self):
        response = self.client.get('/panorama/opnamelocatie/?lat=52.377&lon=4.8970')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('pano_id', response.data)

    def test_get_nearest_close_radius(self):
        response = self.client.get(
            '/panorama/opnamelocatie/?lat=52.3779561&lon=4.8970701&radius=1000')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_9_2017_CLOSE_BUT_NO_CIGAR')

    def test_get_nearest_close_no_radius_max_date(self):
        response = self.client.get(
            '/panorama/opnamelocatie/?lat=52.35101&lon=4.94433&tot=01-01-2015')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')

    def test_get_nearest_all_parameters(self):
        response = self.client.get(
            '/panorama/opnamelocatie/?lat=52.377958&lon=4.897070&radius=10000&vanaf=2014-01-01&tot=2016')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_3_2015_CLOSE')
