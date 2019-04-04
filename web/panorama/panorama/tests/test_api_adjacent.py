# Project
from . test_api_base import PanoramaApiTest


class AdjacentPanoramaApiTest(PanoramaApiTest):

    def test_get_base_panorama(self):
        response = self.client.get('/panorama/panoramas/PANO_1_2014/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data)
        self.assertEqual(response.data['pano_id'], 'PANO_1_2014')

    def test_filtering_on_date1(self):
        response = self.client.get('/panorama/panoramas/?radius=20&near=4.94444897029152,52.3510468066549&timestamp_before=2015-01-01')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data['_embedded']['panoramas'][0])
        self.assertEqual(response.data['_embedded']['panoramas'][0]['pano_id'], 'PANO_1_2014')

    def test_filtering_on_date2(self):
        test_url = '/panorama/panoramas/?radius=20&near=4.94444897029152,52.3510468066549&timestamp_after=2015-01-01'
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('pano_id', response.data['_embedded']['panoramas'][0])
        self.assertEqual(response.data['_embedded']['panoramas'][0]['pano_id'], 'PANO_3_2015_CLOSE')

