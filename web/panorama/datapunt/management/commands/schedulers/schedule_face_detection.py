import time
import logging

from django.conf import settings

from datasets.panoramas.models import Panorama
from datapunt.management.mixins import PanoramaTableAware
from datapunt.management.queue import Scheduler

log = logging.getLogger(__name__)


class FaceDetectionScheduler(Scheduler, PanoramaTableAware):
    _route_out = 'face_task'

    def schedule(self):
        with self.panorama_table_present():
            while True:
                self.queue_result()
                time.sleep(15)

    def get_messages(self):
        messages = []
        for panorama in Panorama.detected_lp.all()[:50]:
            log.info("Sending face detection task for: {}".format(panorama.pano_id))
            messages.append({'pano_id': panorama.pano_id,
                             'panorama_url': panorama.equirectangular_img_urls['full']
                                                .replace(settings.PANO_IMAGE_URL+'/', '')})
            panorama.status = Panorama.STATUS.detecting1
            panorama.save()

        return messages