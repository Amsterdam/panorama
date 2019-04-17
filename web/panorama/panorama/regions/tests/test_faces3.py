# Python
import logging
import os
from random import randrange
from unittest import TestCase, skipIf

import cv2
from numpy import array, int32

from panorama.regions.faces import FaceDetector
from panorama.regions.util import wrap_around
from panorama.transform import utils_img_file as Img

log = logging.getLogger(__name__)

test_set = [
    # Bijlmer
    # 3 gezichten
    "2016/08/04/TMX7316010203-000045/pano_0000_004366.jpg",
    "2016/08/04/TMX7316010203-000046/pano_0000_000235.jpg",
    "2016/08/04/TMX7316010203-000045/pano_0000_003615.jpg",
    # 4 gezichten
    "2016/08/04/TMX7316010203-000046/pano_0000_000095.jpg",
    "2016/07/07/TMX7315120208-000104/pano_0001_007127.jpg",
    "2016/07/07/TMX7315120208-000104/pano_0001_006789.jpg",
    "2016/07/12/TMX7315120208-000110/pano_0000_005147.jpg",
    # 5 gezichten
    "2016/08/04/TMX7316010203-000045/pano_0000_003995.jpg",
    # 8
    "2016/07/13/TMX7315120208-000121/pano_0001_002923.jpg",
    # Gelderlandplein
    # 3 gezichten
    "2016/06/21/TMX7315080123-000308/pano_0000_000123.jpg",
    "2016/06/21/TMX7315080123-000308/pano_0000_000058.jpg",
    "2016/06/21/TMX7315080123-000307/pano_0000_001971.jpg",
    "2016/06/21/TMX7315080123-000307/pano_0000_001932.jpg",
    # 4 gezichten
    "2016/06/21/TMX7315080123-000307/pano_0000_001966.jpg",
    # Oosterpoort
    # 4 gezichten
    "2016/03/30/TMX7315120208-000023/pano_0000_002097.jpg",
    "2016/05/31/TMX7315120208-000061/pano_0000_000555.jpg",
    "2016/05/12/TMX7315120208-000048/pano_0000_005549.jpg",
    "2016/04/18/TMX7315120208-000029/pano_0000_006384.jpg",
    "2016/04/18/TMX7315120208-000029/pano_0000_006716.jpg",
    # 6 gezichten
    "2016/06/08/TMX7315120208-000071/pano_0006_000345.jpg",
    "2016/04/18/TMX7315120208-000029/pano_0000_006757.jpg",
    # 7 gezichten
    "2016/05/11/TMX7315120208-000047/pano_0000_002318.jpg",
    # 10 gezichten
    "2016/03/30/TMX7315120208-000023/pano_0000_002086.jpg",
]


def draw_lines(image, regions):
    for (lt, rt, rb, lb, detected_by) in regions:
        log.warning("region at: {}, {}, {}, {}, detected by: {}".format(lt, rt, rb, lb, detected_by))

    split_regions = wrap_around(regions)
    for region in split_regions:
        pts = array(region, int32)
        cv2.polylines(image, [pts], True, (0, 255, 0), 2)

    return image


def get_subset():
    test_1 = randrange(0, len(test_set)-1)
    test_2 = randrange(0, len(test_set)-1)

    return [test_set[test_1], test_set[test_2]]


@skipIf(not os.path.exists('/app/test_output'),
        'Face detection test skipped: no mounted directory found, run in docker container')
class TestFaceDetection3(TestCase):
    """
    This is more an integration test than a unit test
    It requires an installed version of opencv, which is available in the container.
    And also: before starting your container set the environment veriable OBJECTSTORE_PASSWORD

        docker exec -it panorama_web_1 ./manage.py test panorama.regions.tests.test_faces3

    Because it's slow not all images are tested all the time.
    look into the .gitignore-ed directory PROJECT/test_output for a visual check of the result
    """
    def test_detection_faces3_runs_without_errors(self):
        for pano_idx, panorama_path in enumerate(get_subset()):
            log.warning("Detecting faces in panorama nr. {}: {}".format(pano_idx, panorama_path))
            fd = FaceDetector(panorama_path)
            found_faces = fd.get_vision_api_face_regions()

            full_image = Img.get_intermediate_panorama_image(panorama_path)
            image = cv2.cvtColor(array(full_image), cv2.COLOR_RGB2BGR)

            image = draw_lines(image, found_faces)

            cv2.imwrite("/app/test_output/face_detection3_{}.jpg".format(pano_idx), image)
