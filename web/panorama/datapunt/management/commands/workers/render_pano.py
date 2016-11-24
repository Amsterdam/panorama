import json, time
from random import randrange

from datapunt.management.queue import Worker


class RenderPano(Worker):
    _route = 'render_pano'
    _route_out = 'pano_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))
        time.sleep(randrange(10, 20))

        return [{ 'pano_id': message_dict['pano_id']}]
