import json
import logging

from panorama.tasks.queue import BaseWorker
from job import render

log = logging.getLogger(__name__)


class RenderPano(BaseWorker):
    _route = 'render_task'
    _route_out = 'rendering_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))
        panorama_path = message_dict['panorama_path']
        panorama_heading = message_dict['panorama_heading']
        panorama_pitch = message_dict['panorama_pitch']
        panorama_roll = message_dict['panorama_roll']

        render(panorama_path, panorama_heading, panorama_pitch, panorama_roll)

        log.warning("done rendering")
        return [{'pano_id': message_dict['pano_id']}]
