from numpy import arange, meshgrid, float64
import numpy as np

from . import utils_img_file as Img
from . import utils_math_array as Math
from .transformer import SOURCE_WIDTH, PANO_HEIGHT


def rotate(im, heading, pitch, roll, target_width=SOURCE_WIDTH):
    im = np.asarray(im).transpose([2, 0, 1])
    r = Math.rotation_matrix(heading, pitch, roll)
    x, y = _rotation_grid(r, target_width)
    return Img.sample_rgb_array_image_as_array(x, y, im)


def _rotation_grid(rot, w: int):
    """Transform a rotation matrix into a sample grid with width w."""
    assert rot.shape == (3, 3)

    x, y = _sample_grid(w)
    # Transform image coordinates in equirectangular projection to cartesian
    # vectors with r=1.
    x, y, z = Math.cartesian_from_cylindrical(x, y)
    x, y, z = Math.rotate_cartesian_vectors((x, y, z), rot)
    # Transform cartesian vectors back to equirectangular image coordinates.
    x, y = Math.cartesian2cylindrical(
        (x, y, z), source_width=SOURCE_WIDTH, source_height=PANO_HEIGHT
    )
    return x, y


def _sample_grid(target_width):
    left_top_x = 0
    left_top_y = 0
    right_bottom_x = SOURCE_WIDTH
    right_bottom_y = PANO_HEIGHT

    steps = SOURCE_WIDTH / target_width

    return (
        arange(left_top_x, right_bottom_x, steps, dtype=float64),
        arange(left_top_y, right_bottom_y, steps, dtype=float64),
    )
