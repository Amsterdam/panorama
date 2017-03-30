import time
import logging

from datasets.panoramas.models import Panorama
from panorama.tasks.mixins import PanoramaTableAware
from panorama.tasks.queue import BaseScheduler

log = logging.getLogger(__name__)


class FaceDetection2Scheduler(BaseScheduler, PanoramaTableAware):
    _route_out = 'detect_face2_task'

    def schedule(self):
        with self.panorama_table_present():
            while True:
                self.queue_result()
                time.sleep(15)

    def get_messages(self):
        messages = []
        for panorama in Panorama.detected_1.all()[:100]:
            log.info("Sending face_detect2 task: {}".format(panorama.pano_id))
            messages.append({'pano_id': panorama.pano_id,
                             'panorama_path': panorama.get_intermediate_url()})
            panorama.status = Panorama.STATUS.detecting2
            panorama.save()

        return messages
