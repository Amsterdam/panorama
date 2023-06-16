import cv2
import numpy as np

from panorama.regions.util import wrap_around


def dict_from(region):
    return {
        "left_top_x": region.left_top_x,
        "left_top_y": region.left_top_y,
        "right_top_x": region.right_top_x,
        "right_top_y": region.right_top_y,
        "right_bottom_x": region.right_bottom_x,
        "right_bottom_y": region.right_bottom_y,
        "left_bottom_x": region.left_bottom_x,
        "left_bottom_y": region.left_bottom_y,
    }


def blur(im, regions):
    """Blur regions in the Image im."""
    blurred_image = np.array(im)

    # blur regions
    for region in _split_regions(regions):
        (top, left), (bottom, right) = _make_rectangle(region)
        snippet = blurred_image[top:bottom, left:right]
        blur_kernel_size = 2 * int((bottom - top) / 4) + 1
        snippet = cv2.GaussianBlur(
            snippet, (blur_kernel_size, blur_kernel_size), blur_kernel_size
        )
        blurred_image[top:bottom, left:right] = snippet

    return blurred_image


def _make_rectangle(points):
    """
    Returns the smallest axis-oriented rectangle that contains all the (x, y) points.
    """
    top = min(p[1] for p in points)
    left = min(p[0] for p in points)
    bottom = max(p[1] for p in points)
    right = max(p[0] for p in points)

    return (top, left), (bottom, right)


def _split_regions(region_dicts):
    split_regions = []
    for region_dict in region_dicts:
        for split_region in wrap_around(
            [
                (
                    (region_dict["left_top_x"], region_dict["left_top_y"]),
                    (region_dict["right_top_x"], region_dict["right_top_y"]),
                    (region_dict["right_bottom_x"], region_dict["right_bottom_y"]),
                    (region_dict["left_bottom_x"], region_dict["left_bottom_y"]),
                    "",
                )
            ]
        ):
            split_regions.append(split_region)

    return split_regions
