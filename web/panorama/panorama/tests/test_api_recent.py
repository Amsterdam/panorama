import logging
# Project
from . test_api_base import PanoramaApiTest

log = logging.getLogger(__name__)


class RecentPanoramaApiTest(PanoramaApiTest):

    def test_list_panoramas(self):
        response = self.client.get('/panorama/panoramas/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(8, len(response.data['_embedded']['panoramas']))
