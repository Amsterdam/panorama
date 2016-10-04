# Python
import io, os, logging
from unittest import TestCase, mock, skipIf

from PIL import Image
from scipy import misc
from django.conf import settings

from datasets.panoramas.regions.license_plates import LicensePlateSampler
from datasets.shared.object_store import ObjectStore

log = logging.getLogger(__name__)
object_store = ObjectStore()


def set_pano(pano):
    global panorama_url
    panorama_url = pano


def mock_get_raw_pano():
    raw_image = object_store.get_datapunt_store_object(panorama_url)
    return Image.open(io.BytesIO(raw_image))


@skipIf(not os.path.exists('/app/test_output'),
        'Sampling test skipped: no mounted directory found, run in docker container')
class TestImageSampling(TestCase):
    """
    This is more an integration test than a unit test
    It expects a mounted /app/test_output folder, run this in a Docker container

        `docker exec -it panorama_web_1 ./manage.py test datasets.panoramas.regions.tests.test_license_plates`

    look into the .gitignore-ed directory PROJECT/test_output for a visual check on the sampling
    """
    test_set = [
        "2016/04/18/TMX7315120208-000030/pano_0000_000853_normalized.jpg", # 3
        # "2016/05/09/TMX7315120208-000038/pano_0002_000466_normalized.jpg",  # 1
        # "2016/06/09/TMX7315120208-000073/pano_0004_000087_normalized.jpg",  # 2, taxi, buitenlands
        # "2016/05/09/TMX7315120208-000038/pano_0000_000321_normalized.jpg",  # 1
        # "2016/05/26/TMX7315120208-000059/pano_0005_000402_normalized.jpg",  # 1, vallende lijn
        # "2016/06/14/TMX7315120208-000085/pano_0000_002422_normalized.jpg",  # 2, schuin
        # "2016/06/21/TMX7315080123-000304/pano_0000_001220_normalized.jpg",  # 2, waarvan 1 schuin
        # "2016/07/12/TMX7315120208-000110/pano_0000_000175_normalized.jpg",  # 3
        # "2016/07/27/TMX7316060226-000006/pano_0001_001524_normalized.jpg",  # 5
        # "2016/08/02/TMX7316010203-000040/pano_0001_001871_normalized.jpg",  # 6
        # "2016/08/04/TMX7316010203-000046/pano_0000_000743_normalized.jpg",  # 2, misschien 3
        # "2016/03/17/TMX7315120208-000020/pano_0000_000175_normalized.jpg",  # 1
        "2016/08/18/TMX7316010203-000079/pano_0006_000054_normalized.jpg"  # 1
    ]

    @mock.patch('datasets.panoramas.regions.license_plates.LicensePlateSampler._get_raw_image_binary',
                side_effect=mock_get_raw_pano)
    def test_cutting_images_runs_without_errors(self, mock):
        for pano_idx, panorama in enumerate(self.test_set):
            set_pano(panorama)
            cutouts = LicensePlateSampler(None).get_image_samples()
            for img_idx, cutout in enumerate(cutouts):
                img = "/app/test_output/{:02d}_{:03d}.jpg".format(pano_idx, img_idx)
                misc.imsave(img, cutout['image'])

