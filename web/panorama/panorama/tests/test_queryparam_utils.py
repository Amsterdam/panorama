import unittest

from django.utils.datastructures import MultiValueDict

from panorama.queryparam_utils import get_int_value, get_float_value, get_request_coord


class Request(object):

    def __init__(self):
        self.query_params = MultiValueDict()


class TestQueryParamUtilsCoords(unittest.TestCase):

    def test_get_wsg84(self):
        req = Request()
        req.query_params['lat'] = "52.372606"
        req.query_params['lon'] = "4.880097"

        lon, lat = get_request_coord(req.query_params)

        self.assertAlmostEqual(52.372606, lat, places=6)
        self.assertAlmostEqual(4.880097, lon, places=6)

    def test_get_rd(self):
        req = Request()
        req.query_params['x'] = 120467
        req.query_params['y'] = 487313

        lon, lat = get_request_coord(req.query_params)

        self.assertAlmostEqual(52.373, lat, places=3)
        self.assertAlmostEqual(4.880, lon, places=3)


class TestQueryParamUtils(unittest.TestCase):

    def test_get_int_value(self):
        request = Request()
        request.query_params['test'] = '7'

        request_wrong = Request()
        request_wrong.query_params['test'] = 'not_an_int'

        self.assertEquals(7, get_int_value(request, 'test', 8))
        self.assertEquals(8, get_int_value(request, 'not_present', 8))

        self.assertEquals(8, get_int_value(request_wrong, 'test', 8))
        self.assertEquals(8, get_int_value(request_wrong, 'test', 8.0))
        self.assertEquals(8, get_int_value(request_wrong, 'test', '8'))

        self.assertEquals(7, get_int_value(request, 'test', 8, upper=8))
        self.assertEquals(6, get_int_value(request, 'test', 6, upper=6))

        self.assertEquals(7, get_int_value(request, 'test', 8, lower=6))
        self.assertEquals(8, get_int_value(request, 'test', 8, lower=8))

    def test_get_float_value(self):
        request = Request()
        request.query_params['test'] = '7.0'

        request_wrong = Request()
        request_wrong.query_params['test'] = 'not_an_int'

        self.assertEquals(7.0, get_float_value(request, 'test', 8.0))
        self.assertEquals(8.0, get_float_value(request, 'not_present', 8.0))

        self.assertEquals(8.0, get_float_value(request_wrong, 'test', 8))
        self.assertEquals(8.0, get_float_value(request_wrong, 'test', 8.0))
        self.assertEquals(8.0, get_float_value(request_wrong, 'test', '8'))

        self.assertEquals(7.0, get_float_value(request, 'test', 8.0, upper=8.0))
        self.assertEquals(6.0, get_float_value(request, 'test', 6.0, upper=6.0))

        self.assertEquals(7.0, get_float_value(request, 'test', 8.0, lower=6.0))
        self.assertEquals(8.0, get_float_value(request, 'test', 8.0, lower=8.0))


if __name__ == '__main__':
    unittest.main()
