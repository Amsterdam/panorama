from . import img_file_utils as Img
from . import math_utils as Math

# specific property of our pano set source images
SOURCE_WIDTH = 8000     # pixels

# general properties of equirectangular projections
NORTH_0_DEGREES = 0     # default/base heading
PANO_FOV = 360          # field of view in degrees
PANO_HORIZON = 0.5      # fraction of image that is below horizon
PANO_ASPECT = 2         # width over height
PANO_HEIGHT = SOURCE_WIDTH / PANO_ASPECT


class PanoramaTransformer:

    def __init__(self, objectstore_id, heading=0, pitch=0, roll=0):
        self.rotation_matrix = Math.get_rotation_matrix(heading, pitch, roll)
        self.pano_rgb = Img.get_panorama_rgb_array(objectstore_id)

    def get_projection(self):
        pass