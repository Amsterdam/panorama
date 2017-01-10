import logging

# This dependency is only available in the docker container, which has the binaries and bindings installed
import cv2
from scipy import misc

from datasets.shared.object_store import ObjectStore
from datasets.panoramas.transform import utils_img_file as Img

log = logging.getLogger(__name__)
object_store = ObjectStore()


def get_rectangle(region):
    top = min(region['left_top_y'], region['right_top_y'])
    left = min(region['left_top_x'], region['left_bottom_x'])
    bottom = max(region['left_bottom_y'], region['right_bottom_y'])
    right = max(region['right_top_x'], region['right_bottom_x'])

    return (top, left), (bottom, right)


class RegionBlurrer:
    def __init__(self, panorama_path: str):
        """
        :param panorama_path: path of type
                              "2016/08/18/TMX7316010203-000079/pano_0006_000054/equirectangular/panorama_8000.jpg"
        """
        self.panorama_path = panorama_path
        self.panorama_img = Img.get_panorama_image(self.panorama_path)

    def get_blurred_image(self, regions):
        blurred_image = misc.fromimage(self.panorama_img)

        # blur regions
        for region in regions:
            (top, left), (bottom, right) = get_rectangle(region)
            snippet = blurred_image[top:bottom, left:right]
            blur_kernel_size = 2*int((bottom-top)/6)+1
            snippet = cv2.GaussianBlur(snippet, (blur_kernel_size, blur_kernel_size), 0)
            blurred_image[top:bottom, left:right] = snippet

        return blurred_image
