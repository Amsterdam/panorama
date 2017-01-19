#Python
import logging
from random import randint
from unittest import TestCase

from datasets.panoramas.regions.util import wrap_around, get_rectangle, do_split_regions

log = logging.getLogger(__name__)


def get_random_region_for(start_x):
    start_y = randint(1000, 2500)
    width = randint(400, 700)
    region = {
        'left_top_x': start_x,
        'left_top_y': start_y,
        'right_top_x': start_x + width,
        'right_top_y': start_y,
        'right_bottom_x': start_x + width,
        'right_bottom_y': start_y + width,
        'left_bottom_x': start_x,
        'left_bottom_y': start_y + width,
    }
    return region


def get_random_region():
    start_x = randint(0, 8000)
    return get_random_region_for(start_x)


def get_wrap_around_region():
    start_x = 7800
    return get_random_region_for(start_x)


def get_out_of_range_region():
    start_x = 8050
    return get_random_region_for(start_x)


class TestWrapAround(TestCase):
    def test_wrap_around_x(self):
        actual = wrap_around([((7990, 130), (8010, 130), (8010, 230), (7980, 230), '')])
        self.assertEquals(len(actual), 2)

        points_left, points_right = actual

        self.assertEqual(points_left[0][0], 7990)
        self.assertEqual(points_left[1][0], 8000)
        self.assertEqual(points_left[2][0], 8000)
        self.assertEqual(points_left[3][0], 7980)

        self.assertEqual(points_right[0][0], 0)
        self.assertEqual(points_right[1][0], 10)
        self.assertEqual(points_right[2][0], 10)
        self.assertEqual(points_right[3][0], 0)

    def test_wrap_around_y(self):
        actual = wrap_around([((7990, 130), (8010, 140), (8010, 230), (7990, 250), '')])
        self.assertEquals(len(actual), 2)

        points_left, points_right = actual

        self.assertEqual(points_left[0][1], 130)
        self.assertEqual(points_left[1][1], 135)
        self.assertEqual(points_left[2][1], 240)
        self.assertEqual(points_left[3][1], 250)

        self.assertEqual(points_right[0][1], 135)
        self.assertEqual(points_right[1][1], 140)
        self.assertEqual(points_right[2][1], 230)
        self.assertEqual(points_right[3][1], 240)

    def test_wrap_around_all_left(self):
        actual = wrap_around([((7980, 130), (7990, 140), (7995, 230), (7990, 250), '')])
        self.assertEquals(len(actual), 1)

        points = actual[0]

        self.assertEqual(points[0], (7980, 130))
        self.assertEqual(points[1], (7990, 140))
        self.assertEqual(points[2], (7995, 230))
        self.assertEqual(points[3], (7990, 250))

    def test_wrap_around_all_right(self):
        actual = wrap_around([((8010, 130), (8020, 140), (8025, 230), (8015, 250), '')])
        self.assertEquals(len(actual), 1)

        points = actual[0]

        self.assertEqual(points[0], (10, 130))
        self.assertEqual(points[1], (20, 140))
        self.assertEqual(points[2], (25, 230))
        self.assertEqual(points[3], (15, 250))

    def test_wrap_around_x_below_zero(self):
        actual = wrap_around([((-75, 2114), (67, 2126), (67, 2160), (-75, 2149), '')])
        self.assertEquals(len(actual), 2)

        self.assertEqual(actual[0][0], (7925, 2114))
        self.assertEqual(actual[0][1], (8000, 2120))
        self.assertEqual(actual[0][2], (8000, 2154))
        self.assertEqual(actual[0][3], (7925, 2149))

        self.assertEqual(actual[1][0], (0, 2120))
        self.assertEqual(actual[1][1], (67, 2126))
        self.assertEqual(actual[1][2], (67, 2160))
        self.assertEqual(actual[1][3], (0, 2154))

    def test_wrap_around_edge1(self):
        actual = wrap_around([((7996, 2228), (8066, 2212), (8070, 2230), (8000, 2245), '')])
        self.assertEqual(len(actual), 2)
        self.assertEqual(len(actual[0]), 4)
        self.assertEqual(len(actual[1]), 4)

        self.assertEqual(actual[0][0], (7996, 2228))
        self.assertEqual(actual[0][1], (8000, 2228))
        self.assertEqual(actual[0][2], (8000, 2245))
        self.assertEqual(actual[0][3], (8000, 2245))

        self.assertEqual(actual[1][0], (0, 2228))
        self.assertEqual(actual[1][1], (66, 2212))
        self.assertEqual(actual[1][2], (70, 2230))
        self.assertEqual(actual[1][3], (0, 2245))

    def test_wrap_around_edge2(self):
        actual = wrap_around([((8000, 2228), (8066, 2212), (8070, 2230), (7996, 2245), '')])
        self.assertEqual(len(actual), 2)
        self.assertEqual(len(actual[0]), 4)
        self.assertEqual(len(actual[1]), 4)

    def test_wrap_around_edge3(self):
        actual = wrap_around([((7996, 2228), (8000, 2212), (8070, 2230), (7994, 2245), '')])
        self.assertEqual(len(actual), 2)
        self.assertEqual(len(actual[0]), 4)
        self.assertEqual(len(actual[1]), 4)

    def test_wrap_around_edge4(self):
        actual = wrap_around([((7994, 2228), (8066, 2212), (8000, 2230), (7996, 2245), '')])
        self.assertEqual(len(actual), 2)
        self.assertEqual(len(actual[0]), 4)
        self.assertEqual(len(actual[1]), 4)

    def test_wrap_around_edge5(self):
        actual = wrap_around([((8000, 2228), (8060, 2212), (8000, 2230), (7994, 2245), '')])
        self.assertEqual(len(actual), 2)
        self.assertEqual(len(actual[0]), 4)
        self.assertEqual(len(actual[1]), 4)

    def test_wrap_around_edge6(self):
        actual = wrap_around([((7994, 2228), (8000, 2212), (8060, 2230), (8000, 2245), '')])
        self.assertEqual(len(actual), 2)
        self.assertEqual(len(actual[0]), 4)
        self.assertEqual(len(actual[1]), 4)

    def test_wrap_around_edge7(self):
        actual = wrap_around([((8000, 2228), (8000, 2212), (8060, 2230), (7994, 2245), '')])
        self.assertEqual(len(actual), 2)
        self.assertEqual(len(actual[0]), 4)
        self.assertEqual(len(actual[1]), 4)

    def test_wrap_around_edge8(self):
        actual = wrap_around([((7994, 2228), (8060, 2212), (8000, 2230), (8000, 2245), '')])
        self.assertEqual(len(actual), 2)
        self.assertEqual(len(actual[0]), 4)
        self.assertEqual(len(actual[1]), 4)

class TestGetRectangle(TestCase):
    def test_get_rectangle(self):
        fixture = get_random_region()

        expected_left = fixture['left_top_x'] if fixture['left_top_x'] < fixture['right_top_x'] \
            else fixture['right_top_x']
        expected_top = fixture['left_top_y'] if fixture['left_top_y'] < fixture['right_top_y'] \
            else fixture['right_top_y']
        expected_right = fixture['left_bottom_x'] if fixture['left_bottom_x'] > fixture['right_bottom_x'] \
            else fixture['right_bottom_x']
        expected_bottom = fixture['left_bottom_y'] if fixture['left_bottom_y'] > fixture['right_bottom_y'] \
            else fixture['right_bottom_y']

        self.assertEqual(((expected_top, expected_left), (expected_bottom, expected_right)),
                         get_rectangle(fixture))

    def test_get_x_y_shift(self):
        self.assertEqual(((120, 100), (520, 500)),
                         get_rectangle({
                             'left_top_x': 100,
                             'left_top_y': 120,
                             'right_top_x': 400,
                             'right_top_y': 420,
                             'right_bottom_x': 500,
                             'right_bottom_y': 520,
                             'left_bottom_x': 200,
                             'left_bottom_y': 220,
                         }))
        self.assertEqual(((80, 50), (420, 400)),
                         get_rectangle({
                             'left_top_x': 100,
                             'left_top_y': 120,
                             'right_top_x': 400,
                             'right_top_y': 80,
                             'right_bottom_x': 350,
                             'right_bottom_y': 380,
                             'left_bottom_x': 50,
                             'left_bottom_y': 420,
                         }))


class TestMessages(TestCase):
    messages = [{"pano_id": "TMX7316010203-000050_pano_0000_007872",
                 "panorama_url": "2016/08/08/TMX7316010203-000050/pano_0000_007872/equirectangular/panorama_8000.jpg",
                 "regions": [{"left_top_x": 7810, "left_top_y": 2677, "right_top_x": 7998, "right_top_y": 2654,
                              "right_bottom_x": 8004, "right_bottom_y": 2696, "left_bottom_x": 7815,
                              "left_bottom_y": 2721}]
                 },
                {"pano_id": "TMX7315120208-000067_pano_0013_000416",
                 "panorama_url": "2016/06/06/TMX7315120208-000067/pano_0013_000416/equirectangular/panorama_8000.jpg",
                 "regions": [{"left_top_x": 7996, "left_top_y": 2585, "right_top_x": 8139, "right_top_y": 2584,
                              "right_bottom_x": 8145, "right_bottom_y": 2618, "left_bottom_x": 8002,
                              "left_bottom_y": 2620}]}
                ]

    def testMesseages(self):
        for message in self.messages:
            for region in do_split_regions(message['regions']):
                (top, left), (bottom, right) = get_rectangle(region)
