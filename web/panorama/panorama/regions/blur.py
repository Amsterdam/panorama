import logging

# This dependency is only available in the docker container, which has the binaries and bindings installed
import cv2
from scipy import misc

from panorama.shared.object_store import ObjectStore
from panorama.transform import utils_img_file as Img
from panorama.regions.util import get_rectangle, do_split_regions

log = logging.getLogger(__name__)
object_store = ObjectStore()


def dict_from(region):
    return {
        'left_top_x': region.left_top_x,
        'left_top_y': region.left_top_y,
        'right_top_x': region.right_top_x,
        'right_top_y': region.right_top_y,
        'right_bottom_x': region.right_bottom_x,
        'right_bottom_y': region.right_bottom_y,
        'left_bottom_x': region.left_bottom_x,
        'left_bottom_y': region.left_bottom_y
    }


class RegionBlurrer(object):
    """
    Class to blur the regions of a panorama image
    """
    def __init__(self, panorama_path: str):
        """
        :param panorama_path: path of type
                              "2016/08/18/TMX7316010203-000079/pano_0006_000054.jpg"
        """
        self.panorama_path = panorama_path
        self.panorama_img = Img.get_intermediate_panorama_image(self.panorama_path)

    def get_blurred_image(self, regions):
        """
        Get the blurred image of a panoramas
        :param regions: Regions to blur
        :return: PIL image of the panorama with blurred regions
        """
        blurred_image = misc.fromimage(self.panorama_img)

        # blur regions
        for region in do_split_regions(regions):
            (top, left), (bottom, right) = get_rectangle(region)
            snippet = blurred_image[top:bottom, left:right]
            blur_kernel_size = 2*int((bottom-top)/4)+1
            snippet = cv2.GaussianBlur(snippet, (blur_kernel_size, blur_kernel_size), blur_kernel_size)
            blurred_image[top:bottom, left:right] = snippet

        return blurred_image
