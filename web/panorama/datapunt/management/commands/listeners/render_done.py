import logging
import json

from datapunt.management.queue import Listener

log = logging.getLogger(__name__)


class RenderDone(Listener):
    _route = 'render_done'

    def on_message(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))
        log.warn(" Pano done! %r" % message_dict['pano_id'])
