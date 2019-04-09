from . test_api_base import PanoramaApiTest


class AdjacenciesApiTest(PanoramaApiTest):

    def test_get_base_panorama(self):
        response = self.client.get('/panorama/panoramas/PANO_1_2014/adjacencies/')
        self.assertEqual(response.status_code, 200)

        self.assertIn('adjacencies', response.data['_embedded'])
        adjacencies = response.data['_embedded']['adjacencies']
        self_pano = adjacencies[0]

        self.assertIn('pano_id', self_pano)
        self.assertEqual(self_pano['pano_id'], 'PANO_1_2014')

        self.assertEqual(3, len(adjacencies))
        self.assertIn('pano_id', adjacencies[1])
        self.assertIn('angle', adjacencies[1])
        self.assertIn('direction', adjacencies[1])

    def test_filtering_on_date1(self):
        response = self.client.get('/panorama/panoramas/PANO_1_2014/adjacencies/?timestamp_before=2015-01-01')
        self.assertEqual(response.status_code, 200)

        self.assertIn('adjacencies', response.data['_embedded'])
        adjacencies = response.data['_embedded']['adjacencies']
        self_pano = adjacencies[0]

        self.assertIn('pano_id', self_pano)
        self.assertEqual(self_pano['pano_id'], 'PANO_1_2014')

        self.assertEqual(2, len(adjacencies))
        self.assertIn('pano_id', adjacencies[1])
        self.assertEqual(adjacencies[1]['pano_id'], 'PANO_2_2014_CLOSE')

    def test_filtering_on_date2(self):
        response = self.client.get('/panorama/panoramas/PANO_1_2014/adjacencies/?timestamp_after=2015-01-01')
        self.assertEqual(response.status_code, 200)

        self.assertIn('adjacencies', response.data['_embedded'])
        adjacencies = response.data['_embedded']['adjacencies']
        self_pano = adjacencies[0]

        self.assertIn('pano_id', self_pano)
        self.assertEqual(self_pano['pano_id'], 'PANO_3_2015_CLOSE')

        self.assertEqual(1, len(adjacencies))
