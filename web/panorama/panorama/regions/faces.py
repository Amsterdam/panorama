import logging
import os.path

import cv2
import dlib
from google.cloud import vision
import numpy as np
from PIL import Image

from panorama.object_store import ObjectStore
from panorama.transform import utils_img_file as Img

GOOGLE_VISION_MAX_SIZE = 4000000

log = logging.getLogger(__name__)
object_store = ObjectStore()

PANORAMA_WIDTH = 8000
JUST_ABOVE_HORIZON = 1975
LOWEST_EXPECTED_FACE = 2400
SAMPLE_DISTANCE_X = 355
SAMPLE_DISTANCE_Y = 200

OPENCV_ZOOM = [1.41, 1.18, 1.09]

DLIB_ZOOM = [2, 1.83, 1.68, 1.54]
DLIB_THRESHOLD = -0.05
DLIB_UPSCALE = 1

GOOGLE_VISION_ZOOM = 2.05
GOOGLE_VISION_START_HEIGHT = 1750
GOOGLE_VISION_END_HEIGHT = 3050


def derive(faces, x, y, zoom, cascade, scale_factor, neighbours):
    """
    Calculate the coordinates of a detected region in a snippet back to the original coordinates of the
    source equirectangular panorama

    :param faces: list of detected face-regions
    :param x: left-top x of sample
    :param y: left-top y of sample
    :param zoom: zoom of sample
    :param cascade: the filter that has been used to detect faces
    :param scale_factor: the scale factor that has been used to detect faces
    :param neighbours: the amount of neighbours to detect faces
    :return: a set consisting of 4 coordinate sets, and a description
    """
    derived = []
    detected_by = "cascade={}, scaleFactor={}, neighbours={}, zoom={}".format(cascade, scale_factor, neighbours, zoom)
    for (x0, y0, width, height) in faces:
        x1 = int(x0 / zoom) + x
        y1 = int(y0 / zoom) + y
        w1 = int(width / zoom)
        h1 = int(height / zoom)
        derived.append([(x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1), (x1, y1 + h1), detected_by])
    return derived


class FaceDetector(object):
    def __init__(self, panorama_path: str):
        """
        :param panorama_path: path of type
                              "2016/08/18/TMX7316010203-000079/pano_0006_000054/equirectangular/panorama_8000.jpg"
        """
        self.panorama_path = panorama_path
        self.panorama_img = None

    def get_opencv_face_regions(self):
        """
        Detect face regions with OpenCV
        :return: list of Regions
        """
        self._assert_image_loaded()
        return list(from_opencv(self.panorama_img))

    def _assert_image_loaded(self):
        if self.panorama_img is None:
            self.panorama_img = Img.get_intermediate_panorama_image(self.panorama_path)

    def get_dlib_face_regions(self):
        """
        Detect face regions with DLIB
        :return: list of Regions
        """
        self._assert_image_loaded()
        return list(_dlib_face_regions(self.panorama_img))

    def get_vision_api_face_regions(self):
        """
        Detect face regions with Google Vision API
        :return: list of Regions
        """
        self._assert_image_loaded()
        face_regions = []

        strip = self.panorama_img.crop((0, GOOGLE_VISION_START_HEIGHT, PANORAMA_WIDTH, GOOGLE_VISION_END_HEIGHT))
        google_image_height = GOOGLE_VISION_END_HEIGHT - GOOGLE_VISION_START_HEIGHT

        zoom = GOOGLE_VISION_ZOOM
        zoomed_size = (int(zoom * PANORAMA_WIDTH), int(zoom * google_image_height))
        zoomed = strip.resize(zoomed_size, Image.BICUBIC)

        upload = Img.image2byte_array_sized(zoomed, size=GOOGLE_VISION_MAX_SIZE)

        vision_client = vision.ImageAnnotatorClient()
        image = vision.types.Image(content=upload)

        response = vision_client.face_detection(image=image)

        regions = []
        for fa in response.face_annotations:
            lt, _, rb, _ =  fa.bounding_poly.vertices
            regions.append((lt.x, lt.y,
                            rb.x - lt.x, rb.y - lt.y))

            derived = derive(regions, 0, GOOGLE_VISION_START_HEIGHT, zoom, 'google_vision api', 1, 'no treshold')
            face_regions.extend(derived)

        return face_regions


def _dlib_face_regions(im):
    """Detect face regions with DLIB. Returns a generator of Regions."""
    detector = dlib.get_frontal_face_detector()

    for zoom in DLIB_ZOOM:
        strip = im.crop((0, 1975, im.width, 2600))
        zoomed_size = (int(zoom * im.width), int(zoom * 625))
        zoomed = strip.resize(zoomed_size, Image.BICUBIC)

        detected_faces, _, _ = detector.run(
            np.asarray(zoomed), DLIB_UPSCALE, DLIB_THRESHOLD
        )
        regions = (
            (d.left(), d.top(), d.right() - d.left(), d.bottom() - d.top())
            for d in detected_faces
        )
        yield from derive(
            regions, 0, 1975, zoom, "dlib", DLIB_UPSCALE, ">{}".format(DLIB_THRESHOLD)
        )


_opencv_configs = [
    ("haarcascade_frontalface_default.xml", 1.29, 7, False, "default"),
    ("haarcascade_frontalface_alt.xml", 1.22, 5, False, "alt"),
    ("haarcascade_frontalface_alt2.xml", 1.22, 5, False, "alt2"),
    ("haarcascade_profileface.xml", 1.11, 5, False, "profile"),
    ("haarcascade_profileface.xml", 1.11, 5, True, "profile_flip_correct"),
    ("haarcascade_frontalface_alt_tree.xml", 1.025, 2, False, "alt_tree"),
]

__opencv_classifiers = None


def _opencv_classifiers():
    """Return our cached list of OpenCV Haar cascade classifiers."""
    global __opencv_classifiers

    if __opencv_classifiers is not None:
        return __opencv_classifiers

    __opencv_classifiers = [
        (
            cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, filename)),
            scale,
            min_neighb,
            flip,
            name,
        )
        for filename, scale, min_neighb, flip, name in _opencv_configs
    ]
    return __opencv_classifiers


def from_opencv(im):
    """Detect face regions with OpenCV.
    :return: generator of Regions
    """
    for x in range(0, im.width, SAMPLE_DISTANCE_X):
        for y, zoom in zip(range(JUST_ABOVE_HORIZON, LOWEST_EXPECTED_FACE, SAMPLE_DISTANCE_Y), OPENCV_ZOOM):
            snippet = Img.sample_image(im, x, y)
            snippet = Img.prepare_img(snippet, zoom)
            for classif, scale, min_neighb, flip, name in _opencv_classifiers():
                regions = _opencv_faces(snippet, classif, scale, min_neighb, flip, name)
                yield from derive(regions, x, y, zoom, name, scale, min_neighb)


def _opencv_faces(snippet, classif, scale, min_neighb, flip, name):
    if flip:
        snippet = cv2.flip(snippet, 1)

    faces = classif.detectMultiScale(
        snippet, scaleFactor=scale, minNeighbors=min_neighb,
        flags=cv2.CASCADE_DO_CANNY_PRUNING,
    )

    if flip:
        for face in faces:
            # left_top_x = snippet_width - flipped_left_top_x - width_of_face
            face[0] = snippet.shape[1] - face[0] - face[2]

    if len(faces) > 0:
        log.warning('Cascade {}-{} detected: {}.'.format(scale, name, faces))

    return faces
