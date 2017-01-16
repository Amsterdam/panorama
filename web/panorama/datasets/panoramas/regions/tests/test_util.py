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


class TestSplitRegions(TestCase):
    def test_wrap_around_edge(self):
        edge_region = {'left_top_x': 7996, 'left_top_y': 2228, 'right_top_x': 8066, 'right_top_y': 2212,
                       'right_bottom_x': 8070, 'right_bottom_y': 2230, 'left_bottom_x': 8000, 'left_bottom_y': 2245}
        regions = do_split_regions([edge_region])

        self.assertEqual(len(regions), 2)
        expected0 = {'left_top_x': 7996, 'left_top_y': 2228, 'right_top_x': 8000, 'right_top_y': 2228,
                     'right_bottom_x': 8000, 'right_bottom_y': 2245, 'left_bottom_x': 8000, 'left_bottom_y': 2245}
        expected1 = {'left_top_x': 0, 'left_top_y': 2228, 'right_top_x': 66, 'right_top_y': 2212, 'right_bottom_x': 70,
                     'right_bottom_y': 2230, 'left_bottom_x': 0, 'left_bottom_y': 2245}
        self.assertEqual(expected0, regions[0])
        self.assertEqual(expected1, regions[1])


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
