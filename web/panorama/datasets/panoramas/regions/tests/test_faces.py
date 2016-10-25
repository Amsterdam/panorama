# Python
import io
import logging
import os
from unittest import TestCase, mock, skipIf
import cv2

from PIL import Image
from numpy import array

from datasets.panoramas.regions.faces import FaceDetector
from datasets.shared.object_store import ObjectStore

log = logging.getLogger(__name__)
object_store = ObjectStore()

test_set = [
    "2016/06/07/TMX7315120208-000070/pano_0006_000457/equirectangular/panorama_8000.jpg",
    "2016/06/07/TMX7315120208-000070/pano_0006_000415/equirectangular/panorama_8000.jpg",
    "2016/08/17/TMX7316060226-000030/pano_0008_000377/equirectangular/panorama_8000.jpg",
    "2016/08/17/TMX7316060226-000030/pano_0008_000311/equirectangular/panorama_8000.jpg",
    "2016/08/02/TMX7316060226-000011/pano_0000_001789/equirectangular/panorama_8000.jpg",
    "2016/08/09/TMX7316010203-000053/pano_0000_001613/equirectangular/panorama_8000.jpg",
    "2016/08/08/TMX7316060226-000015/pano_0005_001143/equirectangular/panorama_8000.jpg",
    "2016/08/08/TMX7316060226-000015/pano_0005_001470/equirectangular/panorama_8000.jpg",
    "2016/06/13/TMX7315120208-000075/pano_0000_001549/equirectangular/panorama_8000.jpg",
    "2016/05/17/TMX7315120208-000052/pano_0000_005096/equirectangular/panorama_8000.jpg",
    "2016/04/18/TMX7315120208-000029/pano_0000_001306/equirectangular/panorama_8000.jpg",
    "2016/07/21/TMX7315120208-000158/pano_0000_003364/equirectangular/panorama_8000.jpg",
    "2016/06/21/TMX7315120208-000089/pano_0000_002776/equirectangular/panorama_8000.jpg",
    "2016/05/11/TMX7315120208-000047/pano_0000_001976/equirectangular/panorama_8000.jpg",
    "2016/05/11/TMX7315120208-000047/pano_0000_001975/equirectangular/panorama_8000.jpg",
    "2016/06/01/TMX7315120208-000064/pano_0002_000150/equirectangular/panorama_8000.jpg",
    "2016/03/24/TMX7315120208-000022/pano_0001_000270/equirectangular/panorama_8000.jpg"
]


def set_pano(pano):
    global panorama_url
    panorama_url = pano


def mock_get_raw_pano(ignore):
    raw_image = object_store.get_datapunt_store_object(panorama_url)
    return Image.open(io.BytesIO(raw_image))


@skipIf(not os.path.exists('/app/test_output'),
        'Face detection test skipped: no mounted directory found, run in docker container')
class TestFaceDetection(TestCase):
    """
    This is more an integration test than a unit test
    It requires an installed version of opencv, which is available in the container.
    And also: before starting your container set the environment veriable OBJECTSTORE_PASSWORD

        docker exec -it panorama_web_1 ./manage.py test datasets.panoramas.regions.tests.test_faces

    """
    @mock.patch('datasets.panoramas.regions.faces.get_normalized_image',
                side_effect=mock_get_raw_pano)
    def test_detection_faces_runs_without_errors(self, mock):
        for pano_idx, panorama_url in enumerate(test_set):
            log.warning("Detecting faces in panorama nr. {}: {}".format(pano_idx, panorama_url))
            set_pano(panorama_url)
            image = cv2.cvtColor(array(mock_get_raw_pano(None)), cv2.COLOR_RGB2BGR)

            fd = FaceDetector(None)
            found_faces = fd.get_face_regions()
            for (x, y, w, h) in found_faces:
                log.warning("face at: {}, {}, {}, {}".format(x, y, w, h))
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.imwrite("/app/test_output/face_detection_{}.jpg".format(pano_idx), image)
