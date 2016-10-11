import io

from numpy import array, sqrt, square, dsplit, squeeze, dstack, radians, float64, pi, arctan2, arccos, cos, sin, \
    arange, meshgrid, mod
from scipy import misc
from scipy.ndimage import map_coordinates
from PIL import Image

from datasets.shared.object_store import ObjectStore

# specific property of our pano set source images
SOURCE_WIDTH = 8000     # pixels

# general properties of equirectangular projections
NORTH_0_DEGREES = 0     # default/base heading
PANO_FOV = 360          # field of view in degrees
PANO_HORIZON = 0.5      # fraction of image that is below horizon
PANO_ASPECT = 2         # width over height
PANO_HEIGHT = SOURCE_WIDTH / PANO_ASPECT

# general properties of cubic projections
CUBE_SIDES = ['f', 'b', 'l', 'r', 'u', 'd']
MAX_CUBIC_WIDTH = 2048  # width of cubic edges

class PanoramaTransformer:
    object_store = ObjectStore()

    def __init__(self, panorama_url, heading=0, pitch=0, roll=0):
        self.rotation_matrix = self._get_rotation_matrix(heading, pitch, roll)
        self.pano_rgb = self._get_panorama_rgb_array(panorama_url)

    def get_translated_image(self,
                             target_width=SOURCE_WIDTH,
                             target_fov=PANO_FOV,
                             target_horizon=PANO_HORIZON,
                             target_heading=NORTH_0_DEGREES,
                             target_aspect=PANO_ASPECT):

        # create the target pixel set expressed as coordinates of a normalized equirectangular view of given source-size
        x, y = self._create_sample_set(target_fov, target_aspect, target_heading, target_horizon, target_width)

        # transform image coordinates in equirectangular projection to cartesian vectors with r=1
        x1, y1, z1 = self._cylindrical2cartesian(x, y)

        # rotate vectors according to rotation-matrix for pitch and roll
        x2, y2, z2 = self._rotate_cartesian_vectors(x1, y1, z1)

        # transform cartesion vectors back to image coordinates in a equirectangular projection
        x3, y3 = self._cartesian2cylindrical(x2, y2, z2)

        # sample source image with output meshgrid
        return self._sample_image(x3, y3)

    def get_cubic_projections(self, target_width=MAX_CUBIC_WIDTH):
        cube_projections = {}

        # project to sides
        for direction in CUBE_SIDES:
            # get target pixel set of cube side (cartesian, where r =/= 1, but depends on cube size)
            x, y, z = self._get_cube_side(direction, target_width)

            # rotate vectors according to rotation-matrix for pitch and roll
            x1, y1, z1 = self._rotate_cartesian_vectors(x, y, z)

            # transform cartesion vectors back to image coordinates in a equirectangular projection
            x2, y2 = self._cartesian2cylindrical(x1, y1, z1, r_is_1=False)

            # sample source image with output meshgrid
            cube_projections[direction] = self._sample_image(x2, y2)

        return cube_projections

    def _get_panorama_rgb_array(self, panorama_url):
        # read image as numpy array
        panorama_image = misc.fromimage(self._get_raw_image_binary(panorama_url))

        # split image in 3 channels
        return squeeze(dsplit(panorama_image, 3))

    def _get_rotation_matrix(self, head, pitch, roll):
        r_pitch = radians(pitch)
        r_roll = radians(roll)
        r_yaw = radians(head)

        rx_roll = array(
            [
                [1, 0, 0],
                [0, cos(r_roll), -sin(r_roll)],
                [0, sin(r_roll), cos(r_roll)]
            ],
            dtype=float64
        )
        ry_pitch = array(
            [
                [cos(r_pitch), 0, sin(r_pitch)],
                [0, 1, 0],
                [-sin(r_pitch), 0, cos(r_pitch)]
            ],
            dtype=float64
        )
        rz_yaw = array(
            [
                [cos(r_yaw), -sin(r_yaw), 0],
                [sin(r_yaw), cos(r_yaw), 0],
                [0, 0, 1]
            ],
            dtype=float64
        )

        return rx_roll.dot(ry_pitch).dot(rz_yaw)

    def _create_sample_set(self, target_angle, target_aspect, target_heading, target_horizon, target_width):
        target_center = SOURCE_WIDTH / 2 + target_heading * SOURCE_WIDTH / 360

        chunk_width = SOURCE_WIDTH * target_angle / PANO_FOV
        chunk_height = chunk_width / target_aspect
        chunk_above_horizon = chunk_height * (1 - target_horizon)

        left_top_x = target_center - chunk_width / 2
        left_top_y = (1 - PANO_HORIZON) * PANO_HEIGHT - chunk_above_horizon
        right_bottom_x = left_top_x + chunk_width
        right_bottom_y = left_top_y + chunk_height

        steps = chunk_width / target_width

        return meshgrid(arange(left_top_x, right_bottom_x, steps),
                        arange(left_top_y, right_bottom_y, steps))

    def _cylindrical2cartesian(self, x, y):
        half_width = SOURCE_WIDTH / 2

        phi = (x - half_width) * pi / half_width
        theta = (y * pi) / PANO_HEIGHT

        x1 = sin(theta)*cos(phi)
        y1 = sin(theta)*sin(phi)
        z1 = cos(theta)

        return x1, y1, z1

    def _rotate_cartesian_vectors(self, x, y, z):
        m = self.rotation_matrix

        # perform matrix multiplication
        x1 = m[0][0] * x + m[0][1] * y + m[0][2] * z
        y1 = m[1][0] * x + m[1][1] * y + m[1][2] * z
        z1 = m[2][0] * x + m[2][1] * y + m[2][2] * z

        return x1, y1, z1

    def _cartesian2cylindrical(self, x, y, z, r_is_1=True):
        r = 1 if r_is_1 else sqrt(square(x) + square(y) + square(z))

        theta = arccos(z/r)
        phi = arctan2(y, x)

        half_width = SOURCE_WIDTH / 2

        x1 = mod(half_width + half_width * phi / pi, SOURCE_WIDTH-1)
        y1 = PANO_HEIGHT * theta / pi

        return x1, y1

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

    def _get_raw_image_binary(self, panorama_url):
        raw_image = self.object_store.get_panorama_store_object(panorama_url)
        return Image.open(io.BytesIO(raw_image))

    def _sample_image(self, x, y):
        # resample each channel of the source image
        r = map_coordinates(self.pano_rgb[0], [y, x], order=1)
        g = map_coordinates(self.pano_rgb[1], [y, x], order=1)
        b = map_coordinates(self.pano_rgb[2], [y, x], order=1)

        # merge channels
        return dstack((r, g, b))
