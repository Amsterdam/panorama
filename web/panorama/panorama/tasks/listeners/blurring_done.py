import logging
import json

from panorama.tasks.queue import Listener
from datasets.panoramas.models import Panorama

log = logging.getLogger(__name__)


class BlurDone(Listener):
    _route = 'blur_done'

    def on_message(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        panorama = Panorama.objects.get(pano_id=message_dict['pano_id'])
        panorama.status = Panorama.STATUS.blurred
        panorama.save()

        log.warning("*Blurring* done! %r" % message_dict['pano_id'])
