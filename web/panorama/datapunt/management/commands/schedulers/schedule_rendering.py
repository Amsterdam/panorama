import time
import logging

from datasets.panoramas.models import Panorama
from datapunt.management.mixins import PanoramaTableAware
from datapunt.management.queue import Scheduler

log = logging.getLogger(__name__)


class RenderScheduler(Scheduler, PanoramaTableAware):
    _route_out = 'render_pano'

    def schedule(self):
        with self.panorama_table_present():
            while True:
                self.queue_result()
                time.sleep(240)

    def get_messages(self):
        messages = []
        for panorama in Panorama.to_be_rendered.all()[:5]:
            log.info("Sending render task: {}".format(panorama.pano_id))

            messages.append({'pano_id': panorama.pano_id,
                             'pano_path': panorama.path+panorama.filename,
                             'heading': panorama.heading,
                             'pitch': panorama.pitch,
                             'roll': panorama.roll})

            panorama.status = Panorama.STATUS.rendering
            panorama.save()

        return messages
