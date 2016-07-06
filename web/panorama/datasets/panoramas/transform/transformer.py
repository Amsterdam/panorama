from numpy import array, radians, float64, pi, arctan2, arccos, cos, sin, arange, meshgrid, mod, rint
from scipy import misc


#   general property of pano set source image
SOURCE_WIDTH = 8000             # pixels

# properties of equirectangular projections
PANO_ANGLE = 360              # degrees
PANO_HORIZON = 0.5            # fraction of image that is below horizon
PANO_ASPECT = 2               # width over height
PANO_HEIGHT = SOURCE_WIDTH / PANO_ASPECT


class PanoramaTransformer:

    def __init__(self, panorama):
        self.panorama = panorama

    def get_translated_image(self,
                             target_width=4000,
                             target_angle=360,
                             target_horizon=0.5,
                             target_heading=0,
                             target_aspect=2):

        # create the target pixel set expressed as coordinates of a normalized equirectangular view of given source-size
        x, y = self.create_sample_set(target_angle, target_aspect, target_heading, target_horizon, target_width)

        # transform image coordinates in equirectangular projection to cartesian vectors with r=1
        x1, y1, z1 = self.cylindrical2cartesian(x, y)

        # rotate vectors according to rotation-matrix for pitch and roll
        m = self.get_rotation_matrix(self.panorama.pitch, self.panorama.roll)

        x2 = m[0][0] * x1 + m[0][1] * y1 + m[0][2] * z1
        y2 = m[1][0] * x1 + m[1][1] * y1 + m[1][2] * z1
        z2 = m[2][0] * x1 + m[2][1] * y1 + m[2][2] * z1

        # transform cartesion vectors back to image coordinates in a equirectangular projection
        x3, y3 = self.cartesian2cylindrical(x2, y2, z2)

        # return grid of output pixels from source image based on warped coordinates
        return misc.imread(self.panorama.path+self.panorama.filename)[y3[:, :], x3[:, :]]

    def create_sample_set(self, target_angle, target_aspect, target_heading, target_horizon, target_width):
        target_center = SOURCE_WIDTH / 2 - (self.panorama.heading - target_heading) * SOURCE_WIDTH / 360

        chunk_width = SOURCE_WIDTH * target_angle / PANO_ANGLE
        chunk_height = chunk_width / target_aspect
        chunk_above_horizon = chunk_height * (1 - target_horizon)

        left_top_x = target_center - chunk_width / 2
        left_top_y = (1 - PANO_HORIZON) * PANO_HEIGHT - chunk_above_horizon
        right_bottom_x = left_top_x + chunk_width
        right_bottom_y = left_top_y + chunk_height

        steps = chunk_width / target_width

        return meshgrid(arange(left_top_x, right_bottom_x, steps),
                           arange(left_top_y, right_bottom_y, steps))

    def cylindrical2cartesian(self, x, y):
        phi = (x - PANO_HEIGHT) * pi / PANO_HEIGHT
        theta = (y * pi) / PANO_HEIGHT

        x1 = sin(theta)*cos(phi)
        y1 = sin(theta)*sin(phi)
        z1 = cos(theta)

        return x1, y1, z1

    def get_rotation_matrix(self, pitch, roll):
        pitch_rad = radians(pitch)
        roll_rad = radians(roll)

        pitch_matrix = array([[cos(pitch_rad), 0, sin(pitch_rad)],
                                 [0, 1, 0],
                                 [-1 * sin(pitch_rad), 0, cos(pitch_rad)]],
                                dtype=float64)
        roll_matrix = array([[1, 0, 0],
                                [0, cos(roll_rad), -1 * sin(roll_rad)],
                                [0, sin(roll_rad), cos(roll_rad)]],
                               dtype=float64)

        return pitch_matrix.dot(roll_matrix)

    def cartesian2cylindrical(self, x, y, z):
        theta1 = arccos(z)
        phi1 = arctan2(y, x)

        x1 = mod(rint(PANO_HEIGHT + PANO_HEIGHT * phi1 / pi), SOURCE_WIDTH).astype(int)
        y1 = mod(rint(PANO_HEIGHT * theta1 / pi), PANO_HEIGHT).astype(int)

        return x1, y1

