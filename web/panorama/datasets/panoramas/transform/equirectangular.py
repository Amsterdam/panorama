from numpy import arange, meshgrid

from . import utils_img_file as Img
from . import utils_math_array as Math
from . transformer import SOURCE_WIDTH, PANO_FOV, PANO_HORIZON, NORTH_0_DEGREES, PANO_HEIGHT, PANO_ASPECT, \
    PanoramaTransformer


class EquirectangularTransformer(PanoramaTransformer):

    def get_projection(self,
                       target_width=SOURCE_WIDTH,
                       target_fov=PANO_FOV,
                       target_horizon=PANO_HORIZON,
                       target_heading=NORTH_0_DEGREES,
                       target_aspect=PANO_ASPECT):

        # create the target pixel set expressed as coordinates of a normalized equirectangular view of given source-size
        x, y = self._create_sample_set(target_fov, target_aspect, target_heading, target_horizon, target_width)

        # transform image coordinates in equirectangular projection to cartesian vectors with r=1
        x1, y1, z1 = Math.cylindrical2cartesian((x, y), source_width=SOURCE_WIDTH, source_height=PANO_HEIGHT)

        # rotate vectors according to rotation-matrix for pitch and roll
        x2, y2, z2 = Math.rotate_cartesian_vectors((x1, y1, z1), self.rotation_matrix)

        # transform cartesion vectors back to image coordinates in a equirectangular projection
        x3, y3 = Math.cartesian2cylindrical((x2, y2, z2), source_width=SOURCE_WIDTH, source_height=PANO_HEIGHT)

        # sample source image with output meshgrid
        return Img.sample_image((x3, y3), self.pano_rgb)

    def _create_sample_set(self, target_fov, target_aspect, target_heading, target_horizon, target_width):
        target_center = SOURCE_WIDTH / 2 + target_heading * SOURCE_WIDTH / 360

        chunk_width = SOURCE_WIDTH * target_fov / PANO_FOV
        chunk_height = chunk_width / target_aspect
        chunk_above_horizon = chunk_height * (1 - target_horizon)

        left_top_x = target_center - chunk_width / 2
        left_top_y = (1 - PANO_HORIZON) * PANO_HEIGHT - chunk_above_horizon
        right_bottom_x = left_top_x + chunk_width
        right_bottom_y = left_top_y + chunk_height

        steps = chunk_width / target_width

        return meshgrid(arange(left_top_x, right_bottom_x, steps),
                        arange(left_top_y, right_bottom_y, steps))
