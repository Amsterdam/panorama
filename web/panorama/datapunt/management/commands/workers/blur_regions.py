import json
import logging

from PIL import Image

from datapunt.management.queue import Worker
from datasets.panoramas.regions import blur
from datasets.panoramas.transform.cubic import CubicTransformer
from datasets.panoramas.transform import utils_img_file as Img
from datasets.panoramas.transform import utils_img_file_cubic as CubeImg

log = logging.getLogger(__name__)


def save_image_set(panorama_path, array_image):
    # save blurred equirectangular set
    equirectangular_dir = panorama_path[:-17]

    image = Image.fromarray(array_image)
    Img.save_image(image, equirectangular_dir+"panorama_8000.jpg")
    medium_img = image.resize((4000, 2000), Image.ANTIALIAS)
    Img.save_image(medium_img, equirectangular_dir+"panorama_4000.jpg")
    small_img = image.resize((2000, 1000), Image.ANTIALIAS)
    Img.save_image(small_img, equirectangular_dir+"panorama_2000.jpg")

    # save blurred cubic set
    cubic_dir = panorama_path[:-34] + '/cubic'

    cubic_t = CubicTransformer(None, 0, 0, 0, pano_rgb=Img.get_rgb_channels_from_array_image(array_image))
    projections = cubic_t.get_normalized_projection(target_width=CubeImg.MAX_WIDTH)
    CubeImg.save_as_file_set(cubic_dir, projections)


class BlurRegions(Worker):
    _route = 'blur_task'
    _route_out = 'blur_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))
        panorama_path = message_dict['panorama_url']
        region_blurrer = blur.RegionBlurrer(panorama_path)

        # save intermediate - this will be no longer necessary when all intermediates are present
        #   when all are present: the intermediate is input for detection and blurring.
        intermediate_path = 'intermediate/'+panorama_path[:-34]+'.jpg'
        log.warning("saving intermediate: {}".format(intermediate_path))
        Img.save_image(region_blurrer.panorama_img, intermediate_path, in_panorama_store=True)
        log.warning("done saving intermediate: blurring now.")

        regions = message_dict['regions']
        if len(regions) > 0:
            blurred_img = region_blurrer.get_blurred_image(regions)
            save_image_set(panorama_path, blurred_img)

        log.warning("done blurring")
        return [{'pano_id': message_dict['pano_id']}]
