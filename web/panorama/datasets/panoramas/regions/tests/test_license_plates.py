# Python
import io
import logging
import os
from random import randrange
from unittest import TestCase, mock, skipIf

from PIL import Image
from scipy import misc

from datasets.panoramas.regions.license_plates import LicensePlateSampler, LicensePlateDetector
from datasets.shared.object_store import ObjectStore

log = logging.getLogger(__name__)
object_store = ObjectStore()

test_set = [
    "2016/04/18/TMX7315120208-000030/pano_0000_000853_normalized.jpg",  # 3
    "2016/05/09/TMX7315120208-000038/pano_0002_000466_normalized.jpg",  # 1
    "2016/06/09/TMX7315120208-000073/pano_0004_000087_normalized.jpg",  # 2, taxi, buitenlands
    "2016/05/09/TMX7315120208-000038/pano_0000_000321_normalized.jpg",  # 1
    "2016/05/26/TMX7315120208-000059/pano_0005_000402_normalized.jpg",  # 1, vallende lijn
    "2016/06/14/TMX7315120208-000085/pano_0000_002422_normalized.jpg",  # 2, schuin
    "2016/06/21/TMX7315080123-000304/pano_0000_001220_normalized.jpg",  # 2, waarvan 1 schuin
    "2016/07/12/TMX7315120208-000110/pano_0000_000175_normalized.jpg",  # 3
    "2016/07/27/TMX7316060226-000006/pano_0001_001524_normalized.jpg",  # 5
    "2016/08/02/TMX7316010203-000040/pano_0001_001871_normalized.jpg",  # 6
    "2016/08/04/TMX7316010203-000046/pano_0000_000743_normalized.jpg",  # 2, misschien 3
    "2016/03/17/TMX7315120208-000020/pano_0000_000175_normalized.jpg",  # 1
    "2016/08/18/TMX7316010203-000079/pano_0006_000054_normalized.jpg"   # 1
]


def set_pano(pano):
    global panorama_url
    panorama_url = pano


def mock_get_raw_pano():
    raw_image = object_store.get_datapunt_store_object(panorama_url)
    return Image.open(io.BytesIO(raw_image))


def get_subset():
    test_1 = randrange(0, len(test_set))
    test_2 = randrange(0, len(test_set))

    return [test_set[test_1] ,test_set[test_2]]


@skipIf(not os.path.exists('/app/test_output'),
        'Sampling test skipped: no mounted directory found, run in docker container')
class TestImageSampling(TestCase):
    """
    This is more an integration test than a unit test
    It expects a mounted /app/test_output folder, run this in a Docker container
    And last but not least: before starting your container set the environment veriable OBJECTSTORE_PASSWORD

    docker exec -it panorama_web_1 ./manage.py test datasets.panoramas.regions.tests.test_license_plates.TestImageSampling

    look into the .gitignore-ed directory PROJECT/test_output for a visual check on the sampling
    """
    @mock.patch('datasets.panoramas.regions.license_plates.LicensePlateSampler._get_raw_image_binary',
                side_effect=mock_get_raw_pano)
    def test_cutting_images_runs_without_errors(self, mock):
        for pano_idx, panorama in enumerate(get_subset()):
            set_pano(panorama)
            samples = LicensePlateSampler(None).get_image_samples()
            for img_idx, sample in enumerate(samples):
                img = "/app/test_output/{:02d}_{:03d}.jpg".format(pano_idx, img_idx)
                misc.imsave(img, sample['image'])


@skipIf(not os.path.exists('/app/test_output'),
        'LicensePlate detection test skipped: no mounted directory found, run in docker container')
class TestLicensePlateDetector(TestCase):
    """
    This is more an integration test than a unit test
    It requires an installed version of openalpr, which is only available in the container.
    And also: before starting your container set the environment veriable OBJECTSTORE_PASSWORD

        docker exec -it panorama_web_1 ./manage.py test datasets.panoramas.regions.tests.test_license_plates.TestLicensePlateDetector

    Because it's slow not all images are tested all the time.
    """
    @mock.patch('datasets.panoramas.regions.license_plates.LicensePlateSampler._get_raw_image_binary',
                side_effect=mock_get_raw_pano)
    def test_detection_licenseplates_runs_without_errors(self, mock):
        for panorama in get_subset():
            log.warning("detecting license plates in panorama: {}, please hold".format(panorama))

            set_pano(panorama)
            for region in LicensePlateDetector(None).get_licenseplate_regions():
                for coordinates in region:
                    log.warning("x, y = {}, {}".format(coordinates[0], coordinates[1]))
