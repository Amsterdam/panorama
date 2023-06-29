import logging
from math import tan, radians

import openalpr
from PIL import Image

from panorama.transform import utils_img_file as Img

log = logging.getLogger(__name__)

JUST_BELOW_HORIZON = 2050
PLATES_NEAR_BY = 2451
SAMPLE_DISTANCE_H = 355
SAMPLE_DISTANCE_V = 200

ANGLE_RANGE = range(7, 50, 7)

ZOOM1 = 1.5
ZOOM2 = 1.22
ZOOM3 = 1.05


def calculate_shear_data(shear_angle):
    """
        See: https://en.wikipedia.org/wiki/Affine_transformation#/media/File:2D_affine_transformation_matrix.svg
        and: http://stackoverflow.com/questions/14177744/how-does-perspective-transformation-work-in-pil

        We use a vertical shear and stretch the image horizontally to emulate a perspective correction
        Because from these, calculating the original coordinates back is simpler and easier to do
            than from a full blown perspective correction
    """
    shear_factor = tan(radians(shear_angle))
    # we increase the height of the picture to keep every pixel in view
    new_height = int(Img.SAMPLE_HEIGHT + abs(shear_factor) * Img.SAMPLE_WIDTH)
    size = (Img.SAMPLE_WIDTH, new_height)
    # we might also need to shift the image down to keep it in view
    y_offset = Img.SAMPLE_HEIGHT - new_height if shear_angle > 0 else 0
    #   The two first rows of the affine-matrix concatenated
    #       A combination of shear in the y direction and a translation along y to keep it in view
    affine_matrix = (1, 0, 0, shear_factor, 1, y_offset)
    # the more we shear, the more we are looking for a view on the license plate that is likely compressed
    # we widen the image to compensate for that
    widen = 1+abs(shear_factor)
    return widen, size, affine_matrix


def derive(coordinates, x, y, zoom, shear_angle, widen, detected_by):
    """
    Calculate the coordinates of a detected region in a warped image back to the original coordinates of the
    original equirectangular panorama

    :param coordinates: the coordinate-set in the sample image to be calculated back
    :param x: top left-x of the sample
    :param y: top left-y of the sample
    :param zoom: zoom of the sample
    :param shear_angle: shear of the sample
    :param widen: the factor with which the sample has been widened
    :param detected_by: description of the matched region
    :return: coordinateset, including description
    """
    derived = []
    for coordinate_set in coordinates:
        x1 = int(coordinate_set['x']/widen/zoom)
        y1 = int(coordinate_set['y']/zoom)
        if shear_angle >= 0:
            y2 = y1 - (Img.SAMPLE_WIDTH - x1) * tan(radians(shear_angle))
        else:
            y2 = y1 + x1 * tan(radians(shear_angle))
        derived.append((int(x1+x), int(y2+y)))
    derived.append(detected_by)
    return derived


def parse(results, x, y, zoom, shear_angle, widen):
    """
    Parse the results of detection (create set of information that can be fed to Region)

    :param results: array of resultsets
    :param x: top left-x of the sample
    :param y: top left-y of the sample
    :param zoom: zoom of the sample
    :param shear_angle: shear of the sample
    :param widen: the factor with which the sample has been widened
    :return: array of sets for Region
    """
    parsed = []
    detected_by = "shear_angle={}, zoom={}".format(shear_angle, zoom)
    for result in results:
        # exclude the most frequent false positive, when encountering rasters (gates, in walls, etc.)
        if "III" not in result['plate']:
            parsed.append(derive(result['coordinates'], x, y, zoom, shear_angle, widen, detected_by))
    return parsed


def _resize(im: Image.Image, size, widen, zoom):
    """
    Stretch and zoom a sheared image

    :param im: PIL image to stretch
    :param size: set of width and height of the image
    :param widen: the factor to widen the image
    :param zoom: the factor to zoom the image
    :return: PIL image that is resized.
    """
    width = int(size[0] * zoom * widen)
    height = int(size[1] * zoom)
    return im.resize((width, height), Image.BICUBIC)


# Paths after installation of OpenALPR in the Docker image.
OPENALPR_DATA = "/usr/share/openalpr/runtime_data"
OPENALPR_CONF = "/etc/openalpr/openalpr.conf"
LICENSEPLATE_REGION = "eu"


def from_openalpr(im):
    # Loading this takes only milliseconds after the first time,
    # so don't bother caching it.
    alpr = openalpr.Alpr(LICENSEPLATE_REGION, OPENALPR_CONF, OPENALPR_DATA)
    if not alpr.is_loaded():
        # OpenALPR doesn't raise, it just returns an invalid object.
        msg = f"Error loading OpenALPR from {OPENALPR_CONF!r}, {OPENALPR_DATA!r}"
        raise Exception(msg)
    log.info("Using OpenALPR {}".format(alpr.get_version()))

    return list(_from_openalpr(im, alpr))

def _from_openalpr(im, alpr):
    for x in range(0, Img.PANORAMA_WIDTH, SAMPLE_DISTANCE_H):
        for idx, y in enumerate(range(JUST_BELOW_HORIZON, PLATES_NEAR_BY, SAMPLE_DISTANCE_V)):
            zoom = ZOOM1 if idx == 0 else ZOOM2
            snippet = Img.sample_image(im, x, y)
            zoomed_snippet = Img.prepare_img(snippet, zoom, for_cv=False)
            results = alpr.recognize_array(Img.image2byte_array(zoomed_snippet))['results']
            yield from parse(results, x, y, zoom, 0, 1)

            zoom = ZOOM2 if idx == 0 else ZOOM3
            for angle in ANGLE_RANGE:
                for direction in [1, -1]:
                    widen, size, affine_matrix = calculate_shear_data(angle*direction)
                    sheared = snippet.transform(size, Image.AFFINE, affine_matrix, Image.BICUBIC)
                    resized = _resize(sheared, size, widen, zoom)
                    results = alpr.recognize_array(Img.image2byte_array(resized))['results']
                    yield from parse(results, x, y, zoom, angle*direction, widen)
