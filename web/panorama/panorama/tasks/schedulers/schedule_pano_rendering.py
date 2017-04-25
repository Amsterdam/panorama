import logging
import time

from django.conf import settings

from panorama.tasks.mixins import PanoramaTableAware
from panorama.tasks.queue import BaseScheduler
from datasets.panoramas.models import Panorama, Region
from panorama.regions import blur

log = logging.getLogger(__name__)


class RenderScheduler(BaseScheduler, PanoramaTableAware):
    _route_out = 'render_task'

    def schedule(self):
        with self.panorama_table_present():
            while True:
                self.queue_result()
                time.sleep(15)

    def get_messages(self):
        messages = []
        for pano_to_render in Panorama.to_be_rendered.all()[:50]:
            messages.append({'pano_id': pano_to_render.pano_id,
                             'panorama_path': pano_to_render.path+pano_to_render.filename,
                             'panorama_heading': pano_to_render.heading,
                             'panorama_pitch': pano_to_render.pitch,
                             'panorama_roll': pano_to_render.roll})
            log.info("Sending render task: {}".format(pano_to_render.pano_id))

            pano_to_render.status = Panorama.STATUS.rendering
            pano_to_render.save()

        return messages
