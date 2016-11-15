#Python
from unittest import TestCase

# Project
from datasets.panoramas.regions.util import wrap_around


class TestRegions(TestCase):
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
