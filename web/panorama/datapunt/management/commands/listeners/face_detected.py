import logging
import json

from datapunt.management.queue import Listener

log = logging.getLogger(__name__)


class FaceDone(Listener):
    _route = 'face_done'

    def on_message(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))
        log.warn("   Face done! %r" % message_dict['pano_id'])
