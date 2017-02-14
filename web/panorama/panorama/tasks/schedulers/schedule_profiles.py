import time
import logging

from django.conf import settings

from datasets.panoramas.models import Panorama
from panorama.tasks.mixins import PanoramaTableAware
from panorama.tasks.queue import BaseScheduler

log = logging.getLogger(__name__)


class ProfileDetectionScheduler(BaseScheduler, PanoramaTableAware):
    _route_out = 'detect_profile_task'

    def schedule(self):
        with self.panorama_table_present():
            while True:
                self.queue_result()
                time.sleep(15)

    def get_messages(self):
        messages = []
        for panorama in Panorama.detected_2.all()[:100]:
            log.info("Sending profile detect task: {}".format(panorama.pano_id))

            messages.append({'pano_id': panorama.pano_id,
                             'panorama_url': panorama.equirectangular_img_urls['full']
                            .replace(settings.PANO_IMAGE_URL+'/', '')})

            panorama.status = Panorama.STATUS.detecting_profile
            panorama.save()

        return messages
