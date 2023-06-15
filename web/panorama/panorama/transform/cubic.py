from numpy import arange, meshgrid

from . import utils_img_file as Img
from . import utils_math_array as Math
from . transformer import SOURCE_WIDTH, PANO_HEIGHT, BasePanoramaTransformer


CUBE_FRONT, CUBE_BACK, CUBE_LEFT, CUBE_RIGHT, CUBE_UP, CUBE_DOWN = 'f', 'b', 'l', 'r', 'u', 'd'
#   preserve order - the preview.jpg in utils_img_file_set depends on it:
CUBE_SIDES = [CUBE_BACK, CUBE_DOWN, CUBE_FRONT, CUBE_LEFT, CUBE_RIGHT, CUBE_UP]

MAX_CUBIC_WIDTH = 2048  # width of cubic edges


class CubicTransformer(BasePanoramaTransformer):

    def project(self, target_width=MAX_CUBIC_WIDTH):
        cube_projections = {}

        # project to sides
        for direction in CUBE_SIDES:
            # get target pixel set of cube side (cartesian, where r =/= 1, but depends on cube form)
            x, y, z = _get_cube_side(direction, target_width)

            # rotate vectors according to rotation-matrix for pitch and roll
            x1, y1, z1 = Math.rotate_cartesian_vectors((x, y, z), self.rotation_matrix)

            # transform cartesion vectors back to image coordinates in a equirectangular projection
            x2, y2 = Math.cartesian2cylindrical((x1, y1, z1),
                                                source_width=SOURCE_WIDTH,
                                                source_height=PANO_HEIGHT,
                                                r_is_1=False)

            # sample source image with output meshgrid
            cube_projections[direction] = Img.sample_rgb_array_image_as_array((x2, y2), self.pano_rgb)

        return cube_projections

    def get_normalized_projection(self, target_width=MAX_CUBIC_WIDTH):
        cube_projections = {}
        for direction in CUBE_SIDES:
            x2, y2 = Math.cartesian2cylindrical(_get_cube_side(direction, target_width),
                                                source_width=SOURCE_WIDTH,
                                                source_height=PANO_HEIGHT,
                                                r_is_1=False)
            cube_projections[direction] = Img.sample_rgb_array_image_as_array((x2, y2), self.pano_rgb)
        return cube_projections


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
