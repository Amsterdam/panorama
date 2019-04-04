# Project
from . test_api_base import PanoramaApiTest


class OpnameLocatieApiTest(PanoramaApiTest):
    def test_get_by_pano_id(self):
        response = self.client.get('/panorama/panoramas/PANO_1_2014/')
        # Making sure its a 200
        self.assertEqual(response.status_code, 200)
        # Malking sure data is correctly retrieved
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')
        # Testing 404 on non existing id
        response = self.client.get('/panorama/panoramas/PANO_NOT_DEFINED/')
        self.assertEqual(response.status_code, 404)

    def test_get_nearest_from_afar_no_radius(self):
        response = self.client.get('/panorama/panoramas/?near=4,50&radius=250')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('pano_id', response.data)

    def test_get_nearest_from_afar_radius(self):
        response = self.client.get('/panorama/panoramas/?near=4,50&radius=250')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('pano_id', response.data)

    def test_get_nearest_from_afar_no_radius_year(self):
        response = self.client.get('/panorama/panoramas/?near=4,50&timestamp_after=2015-01-01&radius=250')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('pano_id', response.data)

    def test_fieldset_to_spec(self):
        response = self.client.get('/panorama/panoramas/PANO_1_2014/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertIn('geometry', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')
        self.assertNotIn('path', response.data)
        self.assertNotIn('geolocation', response.data)

    def test_get_nearest_close_no_radius(self):
        response = self.client.get('/panorama/panoramas/?near=4.8970,52.37795&radius=250')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data['_embedded']['panoramas'][0])
        self.assertEqual(response.data['_embedded']['panoramas'][0]['pano_id'], 'PANO_7_2016_CLOSE_BUT_NO_CIGAR')

    def test_get_nearest_close_no_radius_but_too_far(self):
        response = self.client.get('/panorama/panoramas/?near=4.8970,52.377&radius=250')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('pano_id', response.data)

    def test_get_nearest_close_radius(self):
        response = self.client.get(
            '/panorama/panoramas/?near=4.8970701,52.3779561&radius=200')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data['_embedded']['panoramas'][0])
        self.assertEqual(response.data['_embedded']['panoramas'][0]['pano_id'], 'PANO_9_2017_CLOSE_BUT_NO_CIGAR')

    def test_get_nearest_close_no_radius_max_date(self):
        response = self.client.get(
            '/panorama/panoramas/?near=4.94433,52.35101&timestamp_before=2015-01-01&radius=250')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data['_embedded']['panoramas'][0])
        self.assertEqual(response.data['_embedded']['panoramas'][0]['pano_id'], 'PANO_1_2014')

    def test_get_nearest_all_parameters(self):
        response = self.client.get(
            '/panorama/panoramas/?near=4.94431,52.35103&radius=250'
            '&timestamp_after=2014-01-01&timestamp_before=2016-01-01')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data['_embedded']['panoramas'][0])
        self.assertEqual(response.data['_embedded']['panoramas'][0]['pano_id'], 'PANO_3_2015_CLOSE')
