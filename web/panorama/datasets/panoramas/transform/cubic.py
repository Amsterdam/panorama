from numpy import arange, meshgrid

from . import img_file_utils as Img
from . import math_utils as Math
from . transformer import SOURCE_WIDTH, PANO_HEIGHT, PanoramaTransformer

# general properties of cubic projections
CUBE_SIDES = ['f', 'b', 'l', 'r', 'u', 'd']
MAX_CUBIC_WIDTH = 2048  # width of cubic edges


class CubicTransformer(PanoramaTransformer):

    def get_projection(self, target_width=MAX_CUBIC_WIDTH):
        cube_projections = {}

        # project to sides
        for direction in CUBE_SIDES:
            # get target pixel set of cube side (cartesian, where r =/= 1, but depends on cube size)
            x, y, z = self._get_cube_side(direction, target_width)

            # rotate vectors according to rotation-matrix for pitch and roll
            x1, y1, z1 = Math.rotate_cartesian_vectors((x, y, z), self.rotation_matrix)

            # transform cartesion vectors back to image coordinates in a equirectangular projection
            x2, y2 = Math.cartesian2cylindrical((x1, y1, z1),
                                                source_width=SOURCE_WIDTH,
                                                source_height=PANO_HEIGHT,
                                                r_is_1=False)

            # sample source image with output meshgrid
            cube_projections[direction] = Img.sample_image((x2, y2), self.pano_rgb)

        return cube_projections

    def _get_cube_side(self, side, width):
        # create the target pixel sets expressed as coordinates of a cubic projection of given cube-size
        # u, d, f, b, l, r = up, down, front, back, left, right

        x, y, z = (0, 0, 0)
        half_width = width / 2

        if side == 'f':
            x = half_width
            y, z = meshgrid(arange(-half_width, half_width, 1),
                            arange(half_width, -half_width, -1))
        elif side == 'b':
            x = -half_width
            y, z = meshgrid(arange(half_width, -half_width, -1),
                            arange(half_width, -half_width, -1))
        elif side == 'l':
            y = -half_width
            x, z = meshgrid(arange(-half_width, half_width, 1),
                            arange(half_width, -half_width, -1))
        elif side == 'r':
            y = half_width
            x, z = meshgrid(arange(half_width, -half_width, -1),
                            arange(half_width, -half_width, -1))
        elif side == 'u':
            z = half_width
            y, x = meshgrid(arange(-half_width, half_width, 1),
                            arange(-half_width, half_width, 1))
        elif side == 'd':
            z = -half_width
            y, x = meshgrid(arange(-half_width, half_width, 1),
                            arange(half_width, -half_width, -1))

        return x, y, z
