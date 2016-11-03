from unittest import TestCase
from random import randint
from datasets.panoramas.transform import thumbnail


class TestThumb(TestCase):

    def test_source_selection(self):
        factor = 12
        fov = randint(20, 80)
        sample_width = fov * factor

        self.assertEqual(thumbnail.choose_source_image_and_width(fov, sample_width), ('full', 8000))
        self.assertEqual(thumbnail.choose_source_image_and_width(fov, sample_width / 2), ('medium', 4000))
        self.assertEqual(thumbnail.choose_source_image_and_width(fov, sample_width / 4), ('small', 2000))

    def test_calculate_crop(self):
        heading = randint(0, 360)
        pixels_per_degree = 2000/360

        actual_crop = thumbnail.calculate_crop(2000, 80, 1.5, heading, 0.5)
        self.assertEqual(actual_crop[0], int(1000 + heading * pixels_per_degree - 1000 * 80/360))
        self.assertEqual(actual_crop[1], 351)
        self.assertAlmostEqual(actual_crop[2], int(actual_crop[0]+2000*80/360), delta=1)
        self.assertEqual(actual_crop[3], 648)

        aspect = randint(10, 30) / 10
        actual_crop = thumbnail.calculate_crop(4000, 80, aspect, 0, 0.5)
        self.assertAlmostEqual(actual_crop[2] - actual_crop[0], 4000*80/360, delta=1)
        self.assertAlmostEqual((actual_crop[2] - actual_crop[0])/(actual_crop[3]-actual_crop[1]), aspect, delta=0.01)

        fov = randint(30, 80)
        actual_crop = thumbnail.calculate_crop(4000, fov, 1.5, 0, 0.5)
        self.assertAlmostEqual(actual_crop[2] - actual_crop[0], 4000*fov/360, delta=1)
        self.assertEqual(actual_crop[0], int(2000*(1 - fov/360)))

        horizon = randint(3, 7) / 10
        height = 4000 * 80 / 540
        actual_crop = thumbnail.calculate_crop(4000, 80, 1.5, 0, horizon)
        self.assertAlmostEqual(actual_crop[1], int(1000 - (1-horizon)*height), delta=1)
        self.assertAlmostEqual(actual_crop[3], actual_crop[1]+height, delta=1)
        self.assertEqual(actual_crop[0], 1555)
        self.assertEqual(actual_crop[2], 2444)
