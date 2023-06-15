import logging

import cv2
import numpy as np

from panorama.regions.util import get_rectangle, do_split_regions

log = logging.getLogger(__name__)


def dict_from(region):
    return {
        'left_top_x': region.left_top_x,
        'left_top_y': region.left_top_y,
        'right_top_x': region.right_top_x,
        'right_top_y': region.right_top_y,
        'right_bottom_x': region.right_bottom_x,
        'right_bottom_y': region.right_bottom_y,
        'left_bottom_x': region.left_bottom_x,
        'left_bottom_y': region.left_bottom_y
    }


def blur(im, regions):
    """Blur regions in the Image im. Acts in-place and returns im."""
    blurred_image = np.asarray(im)

    # blur regions
    for region in do_split_regions(regions):
        (top, left), (bottom, right) = get_rectangle(region)
        snippet = blurred_image[top:bottom, left:right]
        blur_kernel_size = 2*int((bottom-top)/4)+1
        snippet = cv2.GaussianBlur(snippet, (blur_kernel_size, blur_kernel_size), blur_kernel_size)
        blurred_image[top:bottom, left:right] = snippet

    return blurred_image
