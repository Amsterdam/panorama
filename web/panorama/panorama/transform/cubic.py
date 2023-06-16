from numpy import arange, meshgrid

from . import utils_img_file as Img
from . import utils_math_array as Math
from . transformer import SOURCE_WIDTH, PANO_HEIGHT


CUBE_FRONT, CUBE_BACK, CUBE_LEFT, CUBE_RIGHT, CUBE_UP, CUBE_DOWN = 'f', 'b', 'l', 'r', 'u', 'd'
#   preserve order - the preview.jpg in utils_img_file_set depends on it:
CUBE_SIDES = [CUBE_BACK, CUBE_DOWN, CUBE_FRONT, CUBE_LEFT, CUBE_RIGHT, CUBE_UP]

MAX_CUBIC_WIDTH = 2048  # width of cubic edges


def project_cubic(im, rot=None, target_width=MAX_CUBIC_WIDTH):
    """Returns cubic projections of an image, optionally rotating it.

    :return: dictionary mapping CUBE_SIDES to NumPy arrays.
    """
    return {
        side: _project_side(side, im, rot, target_width)
        for side in CUBE_SIDES
    }


def _project_side(side, im, rot, width):
    # get target pixel set of cube side (cartesian, where r =/= 1, but depends on cube form)
    x, y, z = _get_cube_side(side, width)

    # rotate vectors according to rotation-matrix for pitch and roll
    if rot is not None:
        x, y, z = Math.rotate_cartesian_vectors((x, y, z), rot)

    # transform cartesion vectors back to image coordinates in a equirectangular projection
    x, y = Math.cartesian2cylindrical((x, y, z),
                                      source_width=SOURCE_WIDTH,
                                      source_height=PANO_HEIGHT,
                                      r_is_1=False)

    # sample source image with output meshgrid
    return Img.sample_rgb_array_image_as_array(x, y, im)


def _get_cube_side(side, width):
    # create the target pixel sets expressed as coordinates of a cubic projection of given cube-size
    # u, d, f, b, l, r = up, down, front, back, left, right

    x, y, z = (0, 0, 0)
    half_width = width / 2

    if side == CUBE_FRONT:
        x = half_width
        y, z = meshgrid(arange(-half_width, half_width, 1),
                        arange(half_width, -half_width, -1))
    elif side == CUBE_BACK:
        x = -half_width
        y, z = meshgrid(arange(half_width, -half_width, -1),
                        arange(half_width, -half_width, -1))
    elif side == CUBE_LEFT:
        y = -half_width
        x, z = meshgrid(arange(-half_width, half_width, 1),
                        arange(half_width, -half_width, -1))
    elif side == CUBE_RIGHT:
        y = half_width
        x, z = meshgrid(arange(half_width, -half_width, -1),
                        arange(half_width, -half_width, -1))
    elif side == CUBE_UP:
        z = half_width
        y, x = meshgrid(arange(-half_width, half_width, 1),
                        arange(-half_width, half_width, 1))
    elif side == CUBE_DOWN:
        z = -half_width
        y, x = meshgrid(arange(-half_width, half_width, 1),
                        arange(half_width, -half_width, -1))
    else:
        raise ValueError("invalid side")

    return (x, y, z)
