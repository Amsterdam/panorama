# Python
import logging
from random import randrange
from unittest import TestCase

from datasets.panoramas.regions import cliches as cl

log = logging.getLogger(__name__)


class TestCliches(TestCase):
    cliches = cl.Cliches()

    def test_cliches(self):
        self.assertEqual(len(self.cliches.all),
                         (1 + 2 * len(cl.SAMPLE_SHIFTS)) * cl.PANORAMA_ANGLE / cl.SAMPLE_ANGLE)

        for cliche in self.cliches.all:
            self.assertAlmostEquals(cl.SAMPLE_WIDTH * cl.SAMPLE_MAGNIFICATION, len(cliche.x), delta=1)
            self.assertAlmostEquals(cl.SAMPLE_HEIGHT * cl.SAMPLE_MAGNIFICATION, len(cliche.x[0]), delta=1)
            self.assertAlmostEquals(cl.SAMPLE_WIDTH * cl.SAMPLE_MAGNIFICATION, len(cliche.y), delta=1)
            self.assertAlmostEquals(cl.SAMPLE_HEIGHT * cl.SAMPLE_MAGNIFICATION, len(cliche.y[0]), delta=1)

    def test_getting_original_coordinates(self):
        for c_idx, cliche in enumerate(self.cliches.all):
            test_x = randrange(0, len(cliche.x[0]))
            test_y = randrange(0, len(cliche.y))

            expect_y = test_y / cl.SAMPLE_MAGNIFICATION + cliche.y[0][0]
            expect_x = cl.SAMPLE_X + (test_x / cl.SAMPLE_MAGNIFICATION) * (1 - cliche.shift_factor * (expect_y - cliche.y_mid) )

            actual_x, actual_y = cliche.original(test_x, test_y)

            msg = "testing cliche[{}](x, y) = ({}, {}) to map back to ({}, {}), but resulting in ({}, {})".format(
                c_idx, test_x, test_y, expect_x, expect_y, actual_x, actual_y
            )

            self.assertAlmostEquals(expect_y % (cl.PANORAMA_WIDTH - 1), actual_y, delta=2, msg=msg)
            self.assertAlmostEquals(expect_x, actual_x, delta=2, msg=msg)
