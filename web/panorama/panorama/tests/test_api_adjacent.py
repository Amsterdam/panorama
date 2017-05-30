# Project
from . test_api_base import PanoramaApiTest

class AdjacentPanoramaApiTest(PanoramaApiTest):

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
        test_url = '/panorama/opnamelocatie/?lat=52.3510468066549&lon=4.94444897029152&vanaf=2015-01-01'
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_3_2015_CLOSE')
        self.assertIn('adjacent', response.data)
        self.assertFalse(response.data['adjacent'])

    def test_get_recent_panorama(self):
        response = self.client.get('/panorama/recente_opnames/alle/PANO_3_2015_CLOSE/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_3_2015_CLOSE')
        self.assertIn('adjacent', response.data)
        self.assertEqual(0, len(response.data['adjacent']))

    def test_get_recent_panorama_with_adjacency(self):
        response = self.client.get('/panorama/recente_opnames/alle/PANO_8_2017_CLOSE/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_8_2017_CLOSE')
        self.assertIn('adjacent', response.data)
        self.assertEqual(2, len(response.data['adjacent']))

    def test_get_recent2016_panorama(self):
        response = self.client.get('/panorama/recente_opnames/2016/PANO_6_2016_CLOSE/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_6_2016_CLOSE')
        self.assertIn('adjacent', response.data)
        self.assertEqual(1, len(response.data['adjacent']))
        self.assertEqual(2016, response.data['adjacent'][0]['year'])

    def test_get_recent2017_panorama(self):
        response = self.client.get('/panorama/recente_opnames/2017/PANO_8_2017_CLOSE/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_8_2017_CLOSE')
        self.assertIn('adjacent', response.data)
        self.assertEqual(1, len(response.data['adjacent']))
        self.assertEqual(2017, response.data['adjacent'][0]['year'])

