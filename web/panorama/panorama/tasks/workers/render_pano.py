import json

from job import render
from panorama.tasks.queue import BaseWorker


class RenderPano(BaseWorker):
    _route = 'render_pano'
    _route_out = 'pano_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        render(message_dict['pano_path'],
               message_dict['heading'],
               message_dict['pitch'],
               message_dict['roll'])

        return [{'pano_id': message_dict['pano_id']}]
