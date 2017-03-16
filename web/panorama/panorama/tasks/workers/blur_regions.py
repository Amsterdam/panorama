import json
import logging

from panorama.tasks.queue import BaseWorker
from panorama.regions import blur
from panorama.transform import utils_img_file_set as ImgSet

log = logging.getLogger(__name__)


class BlurRegions(BaseWorker):
    _route = 'blur_task'
    _route_out = 'blur_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))
        panorama_path = message_dict['panorama_path']

        region_blurrer = blur.RegionBlurrer(panorama_path)

        regions = message_dict['regions']
        if len(regions) > 0:
            blurred_img = region_blurrer.get_blurred_image(regions)
            ImgSet.save_image_set(panorama_path, blurred_img)

        log.warning("done blurring")
        return [{'pano_id': message_dict['pano_id']}]
