from . test_api_base import PanoramaApiTest


class ApiMetasTest(PanoramaApiTest):

    def test_get_status_health(self):
        """
            Tests Health status
        """
        response = self.client.get('/status/health')
        self.assertEqual(response.status_code, 200)
