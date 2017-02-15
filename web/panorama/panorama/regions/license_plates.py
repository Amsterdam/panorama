from math import tan, radians

from PIL.Image import AFFINE, BICUBIC

from panorama.shared.object_store import ObjectStore
from panorama.transform import utils_img_file as Img

from .openalpr import OpenAlpr

object_store = ObjectStore()

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
        Because from these calculating the original coordinates back is simpler and easier to do
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
    parsed = []
    detected_by = "shear_angle={}, zoom={}".format(shear_angle, zoom)
    for result in results:
        # exclude the most frequent false positive, when encountering rasters (gates, in walls, etc.)
        if "III" not in result['plate']:
            parsed.append(derive(result['coordinates'], x, y, zoom, shear_angle, widen, detected_by))
    return parsed


def resize_sheared(sheared, size, widen, zoom):
    width = size[0] * zoom * widen
    height = size[1] * zoom
    resized = sheared.resize((int(width), int(height)), BICUBIC)
    return resized


class LicensePlateDetector(object):
    def __init__(self, panorama_path: str):
        """
        :param panorama_path: path of type
                              "2016/08/18/TMX7316010203-000079/pano_0006_000054/equirectangular/panorama_8000.jpg"
        """
        self.panorama_path = panorama_path
        self.panorama_img = None

    def get_licenseplate_regions(self):
        self.panorama_img = Img.get_panorama_image(self.panorama_path)
        licenseplate_regions = []
        alpr = OpenAlpr().alpr
        for x in range(0, Img.PANORAMA_WIDTH, SAMPLE_DISTANCE_H):
            for idx, y in enumerate(range(JUST_BELOW_HORIZON, PLATES_NEAR_BY, SAMPLE_DISTANCE_V)):
                zoom = ZOOM1 if idx is 0 else ZOOM2
                snippet = Img.sample_image(self.panorama_img, x, y)
                zoomed_snippet = Img.prepare_img(snippet, zoom, for_cv=False)
                results = alpr.recognize_array(Img.image2byte_array(zoomed_snippet))['results']
                licenseplate_regions.extend(parse(results, x, y, zoom, 0, 1))

                zoom = ZOOM2 if idx is 0 else ZOOM3
                for angle in ANGLE_RANGE:
                    for direction in [1, -1]:
                        widen, size, affine_matrix = calculate_shear_data(angle*direction)
                        sheared = snippet.transform(size, AFFINE, affine_matrix, BICUBIC)
                        resized = resize_sheared(sheared, size, widen, zoom)
                        results = alpr.recognize_array(Img.image2byte_array(resized))['results']
                        licenseplate_regions.extend(parse(results, x, y, zoom, angle*direction, widen))

        return licenseplate_regions
