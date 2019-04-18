# Python
import logging
import os
from random import randrange
from unittest import TestCase, skipIf

# Packages
import cv2
from numpy import array, int32

# Project
from panorama.regions.faces import FaceDetector
from panorama.regions.util import wrap_around
from panorama.transform import utils_img_file as Img

log = logging.getLogger(__name__)

test_set = [
    "2016/06/07/TMX7315120208-000070/pano_0006_000457.jpg",
    "2016/06/07/TMX7315120208-000070/pano_0006_000415.jpg",
    "2016/08/17/TMX7316060226-000030/pano_0008_000377.jpg",
    "2016/08/17/TMX7316060226-000030/pano_0008_000311.jpg",
    "2016/08/02/TMX7316060226-000011/pano_0000_001789.jpg",
    "2016/08/09/TMX7316010203-000053/pano_0000_001613.jpg",
    "2016/08/08/TMX7316060226-000015/pano_0005_001143.jpg",
    "2016/08/08/TMX7316060226-000015/pano_0005_001470.jpg",
    "2016/06/13/TMX7315120208-000075/pano_0000_001549.jpg",
    "2016/05/17/TMX7315120208-000052/pano_0000_005096.jpg",
    "2016/04/18/TMX7315120208-000029/pano_0000_001306.jpg",
    "2016/07/21/TMX7315120208-000158/pano_0000_003364.jpg",
    "2016/06/21/TMX7315120208-000089/pano_0000_002776.jpg",
    "2016/05/11/TMX7315120208-000047/pano_0000_001976.jpg",
    "2016/05/11/TMX7315120208-000047/pano_0000_001975.jpg",
    "2016/06/01/TMX7315120208-000064/pano_0002_000150.jpg",
    "2016/03/24/TMX7315120208-000022/pano_0001_000270.jpg"
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
class TestFaceDetection(TestCase):
    """
    This is more an integration test than a unit test
    It requires an installed version of opencv, which is available in the container.
    And also: before starting your container set the environment veriable OBJECTSTORE_PASSWORD

        docker exec -it panorama_web_1 ./manage.py test panorama.regions.tests.test_faces

    Because it's slow not all images are tested all the time.
    look into the .gitignore-ed directory PROJECT/test_output for a visual check of the result
    """
    def test_detection_faces_runs_without_errors(self):
        for pano_idx, panorama_path in enumerate(get_subset()):
            log.warning("Detecting faces in panorama nr. {}: {}".format(pano_idx, panorama_path))
            fd = FaceDetector(panorama_path)
            found_faces = fd.get_opencv_face_regions()

            full_image = Img.get_intermediate_panorama_image(panorama_path)
            image = cv2.cvtColor(array(full_image), cv2.COLOR_RGB2BGR)
            image = draw_lines(image, found_faces)

            cv2.imwrite("/app/test_output/face_detection_{}.jpg".format(pano_idx), image)
