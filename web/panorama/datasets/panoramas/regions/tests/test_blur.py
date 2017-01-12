# Python
import logging
import os
from random import randint
from unittest import TestCase, skipIf

import cv2
from numpy import array

from datasets.shared.object_store import ObjectStore
from . import test_util
from .. import blur

log = logging.getLogger(__name__)
object_store = ObjectStore()

test_set = [
    "2016/04/18/TMX7315120208-000030/pano_0000_000853/equirectangular/panorama_8000.jpg",  # 3
    "2016/05/09/TMX7315120208-000038/pano_0002_000466/equirectangular/panorama_8000.jpg",  # 1
    "2016/06/09/TMX7315120208-000073/pano_0004_000087/equirectangular/panorama_8000.jpg",  # 2, taxi, buitenlands
    "2016/05/09/TMX7315120208-000038/pano_0000_000321/equirectangular/panorama_8000.jpg",  # 1
    "2016/05/26/TMX7315120208-000059/pano_0005_000402/equirectangular/panorama_8000.jpg",  # 1, vallende lijn
    "2016/06/14/TMX7315120208-000085/pano_0000_002422/equirectangular/panorama_8000.jpg",  # 2, schuin
    "2016/06/21/TMX7315080123-000304/pano_0000_001220/equirectangular/panorama_8000.jpg",  # 2, waarvan 1 schuin
    "2016/07/12/TMX7315120208-000110/pano_0000_000175/equirectangular/panorama_8000.jpg",  # 3
    "2016/07/27/TMX7316060226-000006/pano_0001_001524/equirectangular/panorama_8000.jpg",  # 5
    "2016/08/02/TMX7316010203-000040/pano_0001_001871/equirectangular/panorama_8000.jpg",  # 6
    "2016/08/04/TMX7316010203-000046/pano_0000_000743/equirectangular/panorama_8000.jpg",  # 2, misschien 3
    "2016/03/17/TMX7315120208-000020/pano_0000_000175/equirectangular/panorama_8000.jpg",  # 1
    "2016/08/18/TMX7316010203-000079/pano_0006_000054/equirectangular/panorama_8000.jpg"   # 1
]


def get_random_regions():
    regions = []
    for _ in range(randint(1, 3)):
        region = test_util.get_random_region()
        regions.append(region)

    return regions


@skipIf(not os.path.exists('/app/test_output'),
        'Blurtest skipped: no mounted directory found, run in docker container')
class TestBlur(TestCase):
    """
    This is more an integration test than a unit test
    It requires an installed version of  OpenCV which is (probably) only available in the container.
    And also: before starting your container set the environment veriable OBJECTSTORE_PASSWORD

        docker exec -it panorama_web_1 ./manage.py test datasets.panoramas.regions.tests.test_blur

    look into the .gitignore-ed directory PROJECT/test_output for a visual check of the result
    """
    def test_blur_runs_without_error(self):
        for pano_idx, panorama_path in enumerate(test_set):
            log.warning("blurring panorama {}: {}, please hold".format(pano_idx, panorama_path))
            rb = blur.RegionBlurrer(panorama_path)
            image = rb.get_blurred_image(get_random_regions())
            image = cv2.cvtColor(array(image), cv2.COLOR_RGB2BGR)
            cv2.imwrite("/app/test_output/blur_test_{}.jpg".format(pano_idx), image)

    def test_blur_out_of_range(self):
        panorama_path = test_set[randint(0, len(test_set))]
        log.warning("blurring out of range: {}, please hold".format(panorama_path))
        rb = blur.RegionBlurrer(panorama_path)
        image = rb.get_blurred_image([test_util.get_out_of_range_region()])
        image = cv2.cvtColor(array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite("/app/test_output/blur_test_{}.jpg".format('_out_of_range'), image)

    def test_blur_wrap_around(self):
        panorama_path = test_set[randint(0, len(test_set))]
        log.warning("blurring wrap around: {}, please hold".format(panorama_path))
        rb = blur.RegionBlurrer(panorama_path)
        image = rb.get_blurred_image([test_util.get_wrap_around_region()])
        image = cv2.cvtColor(array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite("/app/test_output/blur_test_{}.jpg".format('_wrap_around'), image)

