import io
import logging

# This dependency is available in the docker container, which has the binaries and bindings installed
import cv2

from numpy import array
from PIL import Image

from datasets.shared.object_store import ObjectStore
from datasets.panoramas.transform import utils_img_file as Img

log = logging.getLogger(__name__)
object_store = ObjectStore()

PANORAMA_WIDTH = 8000
PANORAMA_HEIGHT = 4000
JUST_ABOVE_HORIZON = 1900
LOWEST_EXPECTED_FACE = 2200

SAMPLE_DISTANCE = 455
SAMPLE_WIDTH = 600
SAMPLE_HEIGHT = 450
ZOOM_RANGE = [1.12, 1.26, 1.41]

DEFAULT_MIN_NEIGHBOURS = 6
NORMAL = 1
FLIPPED = -1

cascade_sets = [
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml", 1.21, DEFAULT_MIN_NEIGHBOURS, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml", 1.24, DEFAULT_MIN_NEIGHBOURS-3, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt2.xml", 1.15, DEFAULT_MIN_NEIGHBOURS, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_profileface.xml", 1.067, DEFAULT_MIN_NEIGHBOURS, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_profileface.xml", 1.067, DEFAULT_MIN_NEIGHBOURS, FLIPPED),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt_tree.xml", 1.016, 1, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt_tree.xml", 1.018, 1, NORMAL),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt_tree.xml", 1.02, 1, NORMAL),
]


def derive(faces, x, y, zoom):
    derived = []
    for (x0, y0, width, height) in faces:
        x1 = int(x0/zoom) + x
        y1 = int(y0/zoom) + y
        w1 = int(width/zoom)
        h1 = int(height/zoom)
        derived.append([(x1, y1), (x1+w1, y1), (x1+w1, y1+h1), (x1, y1+h1)])
    return derived


class FaceDetector:
    def __init__(self, panorama_path: str):
        """
        :param panorama_path: path of type
                              "2016/08/18/TMX7316010203-000079/pano_0006_000054/equirectangular/panorama_8000.jpg"
        """
        self.panorama_path = panorama_path

    def get_face_regions(self):
        panorama_img = Image.open(io.BytesIO(object_store.get_datapunt_store_object(self.panorama_path)))
        face_regions = []
        for x in range(0, PANORAMA_WIDTH, SAMPLE_DISTANCE):
            for y in (JUST_ABOVE_HORIZON, LOWEST_EXPECTED_FACE):
                if PANORAMA_WIDTH < x + SAMPLE_WIDTH:
                    intermediate = Img.roll_left(panorama_img, SAMPLE_WIDTH, PANORAMA_WIDTH, PANORAMA_HEIGHT)
                    snippet = intermediate.crop((x-SAMPLE_WIDTH, y, x, y+SAMPLE_HEIGHT))
                else:
                    snippet = panorama_img.crop((x, y, x+SAMPLE_WIDTH, y+SAMPLE_HEIGHT))

                for zoom in ZOOM_RANGE:
                    zoomed_size = (int(zoom*SAMPLE_WIDTH), int(zoom * SAMPLE_HEIGHT))
                    zoomed_snippet = snippet.resize(zoomed_size, Image.BICUBIC)
                    gray_image = cv2.cvtColor(array(zoomed_snippet), cv2.COLOR_RGB2GRAY)
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

                        if len(detected_faces) > 0:
                            log.warning('Cascade {}-{} detected: {}.'.format(cascade_set[1], cascade_set[0], detected_faces))
                            face_regions.extend(derive(detected_faces, x, y, zoom))

        return face_regions
