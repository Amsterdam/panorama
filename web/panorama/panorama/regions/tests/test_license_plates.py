# Python
import logging
import os
from random import randrange
from unittest import TestCase, skipIf

# Packages
import cv2
from numpy import array

# Project
from panorama.regions.license_plates import LicensePlateDetector
from panorama.shared.object_store import ObjectStore
from panorama.transform import utils_img_file as Img
from .test_faces import draw_lines

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


def get_subset():
    test_1 = randrange(0, len(test_set)-1)
    test_2 = randrange(0, len(test_set)-1)

    return [test_set[test_1], test_set[test_2]]


@skipIf(not os.path.exists('/app/test_output'),
        'LicensePlate detection test skipped: no mounted directory found, run in docker container')
class TestLicensePlateDetector(TestCase):
    """
    This is more an integration test than a unit test
    It requires an installed version of openalpr, and OpenCV which are (probably) only available in the container.
    And also: before starting your container set the environment veriable OBJECTSTORE_PASSWORD

        docker exec -it panorama_web_1 ./manage.py test panorama.regions.tests.test_license_plates

    Because it's slow not all images are tested all the time.
    look into the .gitignore-ed directory PROJECT/test_output for a visual check of the result
    """
    def test_detection_licenseplates_runs_without_errors(self):
        for pano_idx, panorama_path in enumerate(get_subset()):
            log.warning("detecting license plates in panorama {}: {}, please hold".format(pano_idx, panorama_path))
            lpd = LicensePlateDetector(panorama_path)
            found_licenseplates = lpd.get_licenseplate_regions()

            full_image = Img.get_panorama_image(panorama_path)
            image = cv2.cvtColor(array(full_image), cv2.COLOR_RGB2BGR)

            image = draw_lines(image, found_licenseplates)

            cv2.imwrite("/app/test_output/licenseplate_detection_{}.jpg".format(pano_idx), image)
