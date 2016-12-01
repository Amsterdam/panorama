import cv2
from numpy import array, int32

from datasets.panoramas.transform import utils_img_file as Img
from datasets.panoramas.regions.util import wrap_around


def save_detected_image(full_image, regions, target_file):
    image = cv2.cvtColor(array(full_image), cv2.COLOR_RGB2BGR)
    image = _draw_lines(image, regions)
    Img.save_array_image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), target_file)


def _draw_lines(image, regions):
    split_regions = wrap_around(regions)
    for region in split_regions:
        pts = array(region, int32)
        cv2.polylines(image, [pts], True, (0, 255, 0), 2)

    return image
