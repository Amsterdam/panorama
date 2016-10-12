from unittest import TestCase
from math import sqrt
import datasets.panoramas.transform.math_utils as Math
from numpy import array_equal, allclose


class TestMath(TestCase):

    def test_cylindrical2cartesion(self):
        result = Math.cylindrical2cartesian((4000, 2000), 8000, 4000)
        self.assertArrayAlmostEquals([1,0,0], result)

        result = Math.cylindrical2cartesian((2000, 2000), 8000, 4000)
        self.assertArrayAlmostEquals([0,-1,0], result)

        result = Math.cylindrical2cartesian((0, 2000), 8000, 4000)
        self.assertArrayAlmostEquals([-1,0,0], result)

        result = Math.cylindrical2cartesian((6000, 2000), 8000, 4000)
        self.assertArrayAlmostEquals([0,1,0], result)

        result = Math.cylindrical2cartesian((4000, 1000), 8000, 4000)
        self.assertArrayAlmostEquals([sqrt(1/2),0,sqrt(1/2)], result)

        result = Math.cylindrical2cartesian((4000, 3000), 8000, 4000)
        self.assertArrayAlmostEquals([sqrt(1/2),0,-sqrt(1/2)], result)

        result = Math.cylindrical2cartesian((2000, 1000), 8000, 4000)
        self.assertArrayAlmostEquals([0,-sqrt(1/2),sqrt(1/2)], result)

        result = Math.cylindrical2cartesian((2000, 3000), 8000, 4000)
        self.assertArrayAlmostEquals([0,-sqrt(1/2),-sqrt(1/2)], result)

        result = Math.cylindrical2cartesian((0, 1000), 8000, 4000)
        self.assertArrayAlmostEquals([-sqrt(1/2),0,sqrt(1/2)], result)

        result = Math.cylindrical2cartesian((0, 3000), 8000, 4000)
        self.assertArrayAlmostEquals([-sqrt(1/2),0,-sqrt(1/2)], result)

        result = Math.cylindrical2cartesian((6000, 1000), 8000, 4000)
        self.assertArrayAlmostEquals([0,sqrt(1/2),sqrt(1/2)], result)

        result = Math.cylindrical2cartesian((6000, 3000), 8000, 4000)
        self.assertArrayAlmostEquals([0,sqrt(1/2),-sqrt(1/2)], result)

    def test_cartesian2cylindrical(self):
        result = Math.cartesian2cylindrical((1, 0, 0), 8000, 4000)
        self.assertArrayAlmostEquals([4000, 2000], result)

        result = Math.cartesian2cylindrical((0, -1, 0), 8000, 4000)
        self.assertArrayAlmostEquals([2000, 2000], result)

        result = Math.cartesian2cylindrical((-1, 0, 0), 8000, 4000)
        self.assertArrayAlmostEquals([1, 2000], result)

        result = Math.cartesian2cylindrical((0, 1, 0), 8000, 4000)
        self.assertArrayAlmostEquals([6000, 2000], result)

        result = Math.cartesian2cylindrical((sqrt(1 / 2), 0, sqrt(1 / 2)), 8000, 4000)
        self.assertArrayAlmostEquals([4000, 1000], result)

        result = Math.cartesian2cylindrical((sqrt(1 / 2), 0, -sqrt(1 / 2)), 8000, 4000)
        self.assertArrayAlmostEquals([4000, 3000], result)

        result = Math.cartesian2cylindrical((0, -sqrt(1 / 2), sqrt(1 / 2)), 8000, 4000)
        self.assertArrayAlmostEquals([2000, 1000], result)

        result = Math.cartesian2cylindrical((0, -sqrt(1 / 2), -sqrt(1 / 2)), 8000, 4000)
        self.assertArrayAlmostEquals([2000, 3000], result)

        result = Math.cartesian2cylindrical((-sqrt(1 / 2), 0, sqrt(1 / 2)), 8000, 4000)
        self.assertArrayAlmostEquals([1, 1000], result)

        result = Math.cartesian2cylindrical((-sqrt(1 / 2), 0, -sqrt(1 / 2)), 8000, 4000)
        self.assertArrayAlmostEquals([1, 3000], result)

        result = Math.cartesian2cylindrical((0, sqrt(1 / 2), sqrt(1 / 2)), 8000, 4000)
        self.assertArrayAlmostEquals([6000, 1000], result)

        result = Math.cartesian2cylindrical((0, sqrt(1 / 2), -sqrt(1 / 2)), 8000, 4000)
        self.assertArrayAlmostEquals([6000, 3000], result)

    def test_get_rotation_matrix(self):
        result = Math.get_rotation_matrix(0, 0, 0)
        self.assertTrue(array_equal(result, [[1,0,0],[0,1,0],[0,0,1]]))

        result = Math.get_rotation_matrix(90, 0, 0)
        self.assertTrue(allclose(result, [[0,-1,0],[1,0,0],[0,0,1]]))

        result = Math.get_rotation_matrix(0, 90, 0)
        self.assertTrue(allclose(result, [[0,0,1],[0,1,0],[-1,0,0]]))

        result = Math.get_rotation_matrix(0, 45, 45)
        self.assertTrue(allclose(result, [[sqrt(1/2),0,sqrt(1/2)],[1/2,sqrt(1/2),-1/2],[-1/2,sqrt(1/2),1/2]]))

    def assertArrayAlmostEquals(self, expected, actual):
        self.assertEqual(len(expected), len(actual), 'not same length')
        for i in range(len(actual)):
            self.assertAlmostEquals(expected[i], actual[i], 6, 'index {} in expected {} and actual {}'.format(i, expected, actual))
