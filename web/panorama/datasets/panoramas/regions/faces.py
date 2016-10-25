import io
import cv2

from django.conf import settings
from numpy import array
from PIL import Image

from datasets.panoramas.models import Panorama
from datasets.shared.object_store import ObjectStore

object_store = ObjectStore()

PANORAMA_WIDTH = 8000
DEFAULT_MIN_NEIGHBOURS = 6
JUST_ABOVE_HORIZON = 1900
LOWEST_EXPECTED_FACE = 2600
NORMAL = 1
FLIPPED = -1

cascade_sets = [
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml", 1.21, DEFAULT_MIN_NEIGHBOURS, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml", 1.24, DEFAULT_MIN_NEIGHBOURS-2, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt2.xml", 1.15, DEFAULT_MIN_NEIGHBOURS, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_profileface.xml", 1.067, DEFAULT_MIN_NEIGHBOURS, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_profileface.xml", 1.067, DEFAULT_MIN_NEIGHBOURS, FLIPPED),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt_tree.xml", 1.016, 1, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt_tree.xml", 1.018, 1, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt_tree.xml", 1.02, 1, NORMAL),
]


def get_normalized_image(panorama: Panorama) -> Image:
    path = panorama.equirectangular_img_urls['full'].replace(settings.PANO_IMAGE_URL, '')
    return Image.open(io.BytesIO(object_store.get_datapunt_store_objects(path)))


class FaceDetector:
    def __init__(self, panorama):
        self.panorama = panorama

    def get_face_regions(self):
        face_regions = []
        image = get_normalized_image(self.panorama)
        image = image.crop((0, JUST_ABOVE_HORIZON, PANORAMA_WIDTH, LOWEST_EXPECTED_FACE))
        gray_image = cv2.cvtColor(array(image), cv2.COLOR_RGB2GRAY)
        for cascade_set in cascade_sets:
            face_cascade = cv2.CascadeClassifier(cascade_set[0])
            if cascade_set[3] is FLIPPED:
                gray_image = cv2.flip(gray_image, 0)

            detected_faces = face_cascade.detectMultiScale(
                gray_image, scaleFactor=cascade_set[1], minNeighbors=cascade_set[2]
            )

            if cascade_set[3] is FLIPPED:
                for detected_face in detected_faces:
                    detected_face[0] = PANORAMA_WIDTH - detected_face[0] - detected_face[2]
                gray_image = cv2.flip(gray_image, 0)

            face_regions.extend(detected_faces)

        for face_region in face_regions:
            face_region[1] += JUST_ABOVE_HORIZON

        return face_regions
