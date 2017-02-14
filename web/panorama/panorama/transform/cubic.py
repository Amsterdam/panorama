from numpy import arange, meshgrid

from . import utils_img_file as Img
from . import utils_math_array as Math
from . import utils_math_cubic as Cube
from . transformer import SOURCE_WIDTH, PANO_HEIGHT, BasePanoramaTransformer


class CubicTransformer(BasePanoramaTransformer):

    def get_projection(self, target_width=Cube.MAX_CUBIC_WIDTH):
        cube_projections = {}

        # project to sides
        for direction in Cube.CUBE_SIDES:
            # get target pixel set of cube side (cartesian, where r =/= 1, but depends on cube form)
            x, y, z = self._get_cube_side(direction, target_width)

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

    def get_normalized_projection(self, target_width=Cube.MAX_CUBIC_WIDTH):
        cube_projections = {}
        for direction in Cube.CUBE_SIDES:
            x2, y2 = Math.cartesian2cylindrical(self._get_cube_side(direction, target_width),
                                                source_width=SOURCE_WIDTH,
                                                source_height=PANO_HEIGHT,
                                                r_is_1=False)
            cube_projections[direction] = Img.sample_rgb_array_image_as_array((x2, y2), self.pano_rgb)
        return cube_projections

    def _get_cube_side(self, side, width):
        # create the target pixel sets expressed as coordinates of a cubic projection of given cube-size
        # u, d, f, b, l, r = up, down, front, back, left, right

        x, y, z = (0, 0, 0)
        half_width = width / 2

        if side == Cube.CUBE_FRONT:
            x = half_width
            y, z = meshgrid(arange(-half_width, half_width, 1),
                            arange(half_width, -half_width, -1))
        elif side == Cube.CUBE_BACK:
            x = -half_width
            y, z = meshgrid(arange(half_width, -half_width, -1),
                            arange(half_width, -half_width, -1))
        elif side == Cube.CUBE_LEFT:
            y = -half_width
            x, z = meshgrid(arange(-half_width, half_width, 1),
                            arange(half_width, -half_width, -1))
        elif side == Cube.CUBE_RIGHT:
            y = half_width
            x, z = meshgrid(arange(half_width, -half_width, -1),
                            arange(half_width, -half_width, -1))
        elif side == Cube.CUBE_UP:
            z = half_width
            y, x = meshgrid(arange(-half_width, half_width, 1),
                            arange(-half_width, half_width, 1))
        elif side == Cube.CUBE_DOWN:
            z = -half_width
            y, x = meshgrid(arange(-half_width, half_width, 1),
                            arange(half_width, -half_width, -1))

        return (x, y, z)
