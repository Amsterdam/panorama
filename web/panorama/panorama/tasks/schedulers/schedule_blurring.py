import logging
import time

from django.conf import settings

from panorama.tasks.mixins import PanoramaTableAware
from panorama.tasks.queue import BaseScheduler
from datasets.panoramas.models import Panorama, Region

log = logging.getLogger(__name__)


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


class BlurScheduler(BaseScheduler, PanoramaTableAware):
    _route_out = 'blur_task'

    def schedule(self):
        with self.panorama_table_present():
            while True:
                self.queue_result()
                time.sleep(15)

    def get_messages(self):
        messages = []
        for panorama in Panorama.detected_profile.all()[:100]:
            log.info("Sending blur task: {}".format(panorama.pano_id))
            regions = []
            for region in Region.objects.filter(panorama=panorama).all():
                regions.append(dict_from(region))

            messages.append({'pano_id': panorama.pano_id,
                             'panorama_url': panorama.equirectangular_img_urls['full']
                            .replace(settings.PANO_IMAGE_URL + '/', ''),
                             'regions': regions})

            panorama.status = Panorama.STATUS.blurring
            panorama.save()

        return messages
