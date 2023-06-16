# Python
import logging
from random import randint
from unittest import TestCase

from panorama.regions.util import wrap_around

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
        self.assertEqual(len(actual), 2)

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
        self.assertEqual(len(actual), 2)

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
        self.assertEqual(len(actual), 1)

        points = actual[0]

        self.assertEqual(points[0], (7980, 130))
        self.assertEqual(points[1], (7990, 140))
        self.assertEqual(points[2], (7995, 230))
        self.assertEqual(points[3], (7990, 250))

    def test_wrap_around_all_right(self):
        actual = wrap_around([((8010, 130), (8020, 140), (8025, 230), (8015, 250), '')])
        self.assertEqual(len(actual), 1)

        points = actual[0]

        self.assertEqual(points[0], (10, 130))
        self.assertEqual(points[1], (20, 140))
        self.assertEqual(points[2], (25, 230))
        self.assertEqual(points[3], (15, 250))

    def test_wrap_around_x_below_zero(self):
        actual = wrap_around([((-75, 2114), (67, 2126), (67, 2160), (-75, 2149), '')])
        self.assertEqual(len(actual), 2)

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

    def test_wrap_around_problem1(self):
        actual = wrap_around([((8002, 2409), (8097, 2444), (8093, 2474), (7998, 2438), '')])
        self.assertEqual(len(actual), 2)
        self.assertEqual(len(actual[0]), 3)
        self.assertEqual(len(actual[1]), 5)

    def test_wrap_around_problem2(self):
        actual = wrap_around([((7600, 2448), (8108, 2492), (7999, 2524), (7500, 2477), '')])
        self.assertEqual(len(actual), 2)
        self.assertEqual(len(actual[0]), 5)
        self.assertEqual(len(actual[1]), 3)
