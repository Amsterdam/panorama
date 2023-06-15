from . import utils_img_file as Img
from . import utils_math_array as Math

# specific property of our pano set source images
SOURCE_WIDTH = 8000     # pixels

# general properties of equirectangular projections
NORTH_0_DEGREES = 0     # default/base heading
PANO_FOV = 360          # field of view in degrees
PANO_HORIZON = 0.5      # fraction of image that is below horizon
PANO_ASPECT = 2         # width over height
PANO_HEIGHT = SOURCE_WIDTH / PANO_ASPECT


class BasePanoramaTransformer(object):
    """
    BaseClass for transforming source panorama images
    """

    def __init__(self, panorama_path=None, heading=0, pitch=0, roll=0, rotation_matrix=None, pano_rgb=None):
        self.rotation_matrix = rotation_matrix if rotation_matrix is not None \
            else Math.rotation_matrix(heading, pitch, roll)
        self.pano_rgb = pano_rgb if pano_rgb is not None else Img.get_raw_panorama_as_rgb_array(panorama_path)

    def project(self):
        raise NotImplementedError()
