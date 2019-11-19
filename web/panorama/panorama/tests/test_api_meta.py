# Python
from unittest import skip
from unittest.mock import Mock
# Packages
from django.http import HttpResponse
from corsheaders.middleware import CorsMiddleware
# Project
from . test_api_base import PanoramaApiTest


class ApiMetasTest(PanoramaApiTest):

    @skip
    def test_get_status_health(self):
        """
            Tests both the pass of database-cursor as well as the missing of db-content
        """
        response = self.client.get('/status/health')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Too few Panoramas', str(response.content))

    def test_cors(self):
        """
        Cross Origin Requests should be allowed.
        """
        request = Mock(path='https://api.data.amsterdam.nl/panorama/panoramas/?lat=52.3779561&lon=4.8970701')
        request.method = 'GET'
        request.is_secure = lambda: True
        request.META = {
            'HTTP_REFERER': 'https://foo.google.com',
            'HTTP_HOST': 'api.data.amsterdam.nl',
            'HTTP_ORIGIN': 'https://foo.google.com',
        }
        response = CorsMiddleware().process_response(request, HttpResponse())
        self.assertTrue('access-control-allow-origin' in response._headers)
        self.assertEquals(
            '*', response._headers['access-control-allow-origin'][1])

