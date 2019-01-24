import logging
# Project
from . test_api_base import PanoramaApiTest

log = logging.getLogger(__name__)


class RecentPanoramaApiTest(PanoramaApiTest):

    def test_list_opnamelocaties(self):
        response = self.client.get('/panorama/opnamelocatie/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(8, len(response.data['results']))

    def test_list_recente_opnames(self):
        response = self.client.get('/panorama/recente_opnames/alle/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(4, len(response.data['results']))
