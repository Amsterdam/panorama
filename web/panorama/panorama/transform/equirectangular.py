from numpy import arange, meshgrid, float64

from . import utils_img_file as Img
from . import utils_math_array as Math
from . transformer import SOURCE_WIDTH, PANO_HEIGHT, BasePanoramaTransformer


class EquirectangularTransformer(BasePanoramaTransformer):

    def project(self, target_width=SOURCE_WIDTH):
        # create the target pixel set expressed as coordinates of a normalized equirectangular view of given source-size
        x, y = _create_sample_set(target_width)

        # transform image coordinates in equirectangular projection to cartesian vectors with r=1
        x1, y1, z1 = Math.cartesian_from_cylindrical(x, y)

        # rotate vectors according to rotation-matrix for pitch and roll
        x2, y2, z2 = Math.rotate_cartesian_vectors((x1, y1, z1), self.rotation_matrix)

        # transform cartesion vectors back to image coordinates in a equirectangular projection
        x3, y3 = Math.cartesian2cylindrical((x2, y2, z2), source_width=SOURCE_WIDTH, source_height=PANO_HEIGHT)

        # sample source image with output meshgrid
        return Img.sample_rgb_array_image_as_array(x3, y3, self.pano_rgb)


def _create_sample_set(target_width):
    left_top_x = 0
    left_top_y = 0
    right_bottom_x = SOURCE_WIDTH
    right_bottom_y = PANO_HEIGHT

    steps = SOURCE_WIDTH / target_width

    return (arange(left_top_x, right_bottom_x, steps, dtype=float64),
            arange(left_top_y, right_bottom_y, steps, dtype=float64))
