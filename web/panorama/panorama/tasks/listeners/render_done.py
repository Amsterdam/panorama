import logging
import json

from panorama.tasks.queue import BaseListener
from datasets.panoramas.models import Panorama

log = logging.getLogger(__name__)


class RenderDone(BaseListener):
    _route = 'render_done'

    def on_message(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        panorama = Panorama.objects.get(pano_id=message_dict['pano_id'])
        panorama.status = Panorama.STATUS.rendered
        panorama.save()

        log.warning(" Pano done! %r" % message_dict['pano_id'])
