# Python
import logging
import os
import os.path
from random import randint
from unittest import TestCase, skipIf

import cv2
import numpy as np
from numpy import array
from numpy.testing import assert_allclose
from PIL import Image

from . import test_util
from .. import blur

log = logging.getLogger(__name__)

test_set = [
    "2016/04/18/TMX7315120208-000030/pano_0000_000853.jpg",  # 3
    "2016/05/09/TMX7315120208-000038/pano_0002_000466.jpg",  # 1
    "2016/06/09/TMX7315120208-000073/pano_0004_000087.jpg",  # 2, taxi, buitenlands
    "2016/05/09/TMX7315120208-000038/pano_0000_000321.jpg",  # 1
    "2016/05/26/TMX7315120208-000059/pano_0005_000402.jpg",  # 1, vallende lijn
    "2016/06/14/TMX7315120208-000085/pano_0000_002422.jpg",  # 2, schuin
    "2016/06/21/TMX7315080123-000304/pano_0000_001220.jpg",  # 2, waarvan 1 schuin
    "2016/07/12/TMX7315120208-000110/pano_0000_000175.jpg",  # 3
    "2016/07/27/TMX7316060226-000006/pano_0001_001524.jpg",  # 5
    "2016/08/02/TMX7316010203-000040/pano_0001_001871.jpg",  # 6
    "2016/08/04/TMX7316010203-000046/pano_0000_000743.jpg",  # 2, misschien 3
    "2016/03/17/TMX7315120208-000020/pano_0000_000175.jpg",  # 1
    "2016/08/18/TMX7316010203-000079/pano_0006_000054.jpg",  # 1
]


def get_random_regions():
    regions = []
    for _ in range(randint(1, 3)):
        region = test_util.get_random_region()
        regions.append(region)

    return regions


@skipIf(
    not os.path.exists("/app/test_output"),
    "Blurtest skipped: no mounted directory found, run in docker container",
)
class TestBlur(TestCase):
    """
    This is more an integration test than a unit test
    It requires an installed version of  OpenCV which is (probably) only available in the container.
    And also: before starting your container set the environment veriable OBJECTSTORE_PASSWORD

        docker exec -it panorama_web_1 ./manage.py test panorama.regions.tests.test_blur

    look into the .gitignore-ed directory PROJECT/test_output for a visual check of the result
    """

    def test_blur_runs_without_error(self):
        for pano_idx, panorama_path in enumerate(test_set):
            log.warning(
                "blurring panorama {}: {}, please hold".format(pano_idx, panorama_path)
            )
            rb = blur.RegionBlurrer(panorama_path)
            image = rb.get_blurred_image(get_random_regions())
            image = cv2.cvtColor(array(image), cv2.COLOR_RGB2BGR)
            cv2.imwrite("/app/test_output/blur_test_{}.jpg".format(pano_idx), image)

    def test_blur_out_of_range(self):
        panorama_path = test_set[randint(0, len(test_set) - 1)]
        log.warning("blurring out of range: {}, please hold".format(panorama_path))
        rb = blur.RegionBlurrer(panorama_path)
        image = rb.get_blurred_image([test_util.get_out_of_range_region()])
        image = cv2.cvtColor(array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite("/app/test_output/blur_test_{}.jpg".format("out_of_range"), image)

    def test_blur_wrap_around(self):
        panorama_path = test_set[randint(0, len(test_set) - 1)]
        log.warning("blurring wrap around: {}, please hold".format(panorama_path))
        rb = blur.RegionBlurrer(panorama_path)
        image = rb.get_blurred_image([test_util.get_wrap_around_region()])
        image = cv2.cvtColor(array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite("/app/test_output/blur_test_{}.jpg".format("wrap_around"), image)


def test_blur():
    here = os.path.dirname(__file__)
    im = Image.open(os.path.join(here, "ppmsca_72874.png"))
    expect = Image.open(os.path.join(here, "ppmsca_72874_blurred.png"))

    blurred = blur.blur(
        im,
        [
            {
                # XXX This encoding is highly redundant.
                "left_top_x": 520,
                "left_bottom_x": 520,
                "left_top_y": 290,
                "right_top_y": 290,
                "left_bottom_y": 452,
                "right_bottom_y": 452,
                "right_top_x": 644,
                "right_bottom_x": 644,
            }
        ],
    )
    assert_allclose(np.asarray(blurred), np.asarray(expect))


def test_make_rectangle():
    assert blur._make_rectangle(
        [
            (100, 120),
            (400, 420),
            (500, 520),
            (200, 220),
        ]
    ) == ((120, 100), (520, 500))

    assert blur._make_rectangle(
        [
            (100, 120),
            (400, 80),
            (350, 380),
            (50, 420),
        ]
    ) == ((80, 50), (420, 400))

    assert blur._make_rectangle(
        [(7600, 2448), (8000, 2482), (8000, 2524), (7999, 2524), (7500, 2477)]
    ) == ((2448, 7500), (2524, 8000))
    assert blur._make_rectangle([(0, 2482), (108, 2492), (0, 2524)]) == (
        (2482, 0),
        (2524, 108),
    )


def test_messages():
    for message in [
        {
            "pano_id": "TMX7316010203-000050_pano_0000_007872",
            "panorama_path": "2016/08/08/TMX7316010203-000050/pano_0000_007872.jpg",
            "regions": [
                {
                    "left_top_x": 7810,
                    "left_top_y": 2677,
                    "right_top_x": 7998,
                    "right_top_y": 2654,
                    "right_bottom_x": 8004,
                    "right_bottom_y": 2696,
                    "left_bottom_x": 7815,
                    "left_bottom_y": 2721,
                }
            ],
        },
        {
            "pano_id": "TMX7315120208-000067_pano_0013_000416",
            "panorama_path": "2016/06/06/TMX7315120208-000067/pano_0013_000416.jpg",
            "regions": [
                {
                    "left_top_x": 7996,
                    "left_top_y": 2585,
                    "right_top_x": 8139,
                    "right_top_y": 2584,
                    "right_bottom_x": 8145,
                    "right_bottom_y": 2618,
                    "left_bottom_x": 8002,
                    "left_bottom_y": 2620,
                }
            ],
        },
    ]:
        for region in blur._split_regions(message["regions"]):
            (top, left), (bottom, right) = blur._make_rectangle(region)
