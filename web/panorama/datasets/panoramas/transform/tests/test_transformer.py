import unittest
from math import sqrt
from datasets.panoramas.transform.transformer import PanoramaTransformer


class test_transformer(unittest.TestCase):

    def test_cylindrical2cartesion(self):
        t = PanoramaTransformer(None)

        result = t.cylindrical2cartesian(4000, 2000)
        self.assertArrayAlmostEquals([1,0,0], result)

        result = t.cylindrical2cartesian(2000, 2000)
        self.assertArrayAlmostEquals([0,-1,0], result)

        result = t.cylindrical2cartesian(0, 2000)
        self.assertArrayAlmostEquals([-1,0,0], result)

        result = t.cylindrical2cartesian(6000, 2000)
        self.assertArrayAlmostEquals([0,1,0], result)

        result = t.cylindrical2cartesian(4000, 1000)
        self.assertArrayAlmostEquals([sqrt(1/2),0,sqrt(1/2)], result)

        result = t.cylindrical2cartesian(4000, 3000)
        self.assertArrayAlmostEquals([sqrt(1/2),0,-sqrt(1/2)], result)

        result = t.cylindrical2cartesian(2000, 1000)
        self.assertArrayAlmostEquals([0,-sqrt(1/2),sqrt(1/2)], result)

        result = t.cylindrical2cartesian(2000, 3000)
        self.assertArrayAlmostEquals([0,-sqrt(1/2),-sqrt(1/2)], result)

        result = t.cylindrical2cartesian(0, 1000)
        self.assertArrayAlmostEquals([-sqrt(1/2),0,sqrt(1/2)], result)

        result = t.cylindrical2cartesian(0, 3000)
        self.assertArrayAlmostEquals([-sqrt(1/2),0,-sqrt(1/2)], result)

        result = t.cylindrical2cartesian(6000, 1000)
        self.assertArrayAlmostEquals([0,sqrt(1/2),sqrt(1/2)], result)

        result = t.cylindrical2cartesian(6000, 3000)
        self.assertArrayAlmostEquals([0,sqrt(1/2),-sqrt(1/2)], result)

    def test_cartesian2cylindrical(self):
        t = PanoramaTransformer(None)

        result = t.cartesian2cylindrical(1,0,0)
        self.assertArrayAlmostEquals([4000, 2000], result)

        result = t.cartesian2cylindrical(0,-1,0)
        self.assertArrayAlmostEquals([2000, 2000], result)

        result = t.cartesian2cylindrical(-1,0,0)
        self.assertArrayAlmostEquals([0, 2000], result)

        result = t.cartesian2cylindrical(0,1,0)
        self.assertArrayAlmostEquals([6000, 2000], result)

        result = t.cartesian2cylindrical(sqrt(1/2),0,sqrt(1/2))
        self.assertArrayAlmostEquals([4000, 1000], result)

        result = t.cartesian2cylindrical(sqrt(1/2),0,-sqrt(1/2))
        self.assertArrayAlmostEquals([4000, 3000], result)

        result = t.cartesian2cylindrical(0,-sqrt(1/2),sqrt(1/2))
        self.assertArrayAlmostEquals([2000, 1000], result)

        result = t.cartesian2cylindrical(0,-sqrt(1/2),-sqrt(1/2))
        self.assertArrayAlmostEquals([2000, 3000], result)

        result = t.cartesian2cylindrical(-sqrt(1/2),0,sqrt(1/2))
        self.assertArrayAlmostEquals([0, 1000], result)

        result = t.cartesian2cylindrical(-sqrt(1/2),0,-sqrt(1/2))
        self.assertArrayAlmostEquals([0, 3000], result)

        result = t.cartesian2cylindrical(0,sqrt(1/2),sqrt(1/2))
        self.assertArrayAlmostEquals([6000, 1000], result)

        result = t.cartesian2cylindrical(0,sqrt(1/2),-sqrt(1/2))
        self.assertArrayAlmostEquals([6000, 3000], result)

    def assertArrayAlmostEquals(self, expected, actual):
        self.assertEqual(len(expected), len(actual), 'not same length')
        for i in range(len(actual)):
            self.assertAlmostEquals(expected[i], actual[i], 6, 'index {} in expected {} and actual {}'.format(i, expected, actual))

if __name__ == '__main__':
    unittest.main()
