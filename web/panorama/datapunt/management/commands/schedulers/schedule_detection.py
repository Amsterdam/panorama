import time
import logging
from random import randrange

from django.conf import settings

from datasets.panoramas.models import Panorama
from datapunt.management.mixins import PanoramaTableAware
from datapunt.management.queue import Scheduler

log = logging.getLogger(__name__)


class DetectionScheduler(Scheduler, PanoramaTableAware):
    _route_out = 'unused'

    def schedule(self):
        with self.panorama_table_present():
            while True:
                messages = self.get_messages()
                log.warn("Scheduling {} panoramas for region detection".format(len(messages)))
                self.schedule_messages('face_task', messages)
                self.schedule_messages('license_plate_task', messages)

                time.sleep(60)

    def get_messages(self):
        messages = []
        for panorama in Panorama.rendered.all()[:1]:
            log.info("Sending detection tasks for: {}".format(panorama.pano_id))
            messages.append({'pano_id': panorama.pano_id,
                             'panorama_url': panorama.equirectangular_img_urls['full']
                                                .replace(settings.PANO_IMAGE_URL+'/', '')})
            panorama.status = Panorama.STATUS.blurring
            panorama.save()

        return messages