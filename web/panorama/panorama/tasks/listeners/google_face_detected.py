import logging
import json

from panorama.tasks.queue import BaseListener
from panorama.tasks.detection import save_regions, region_writer
from datasets.panoramas.models import Panorama

log = logging.getLogger(__name__)


class FaceDone(BaseListener):
    _route = 'face3_done'

    def on_message(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        panorama = Panorama.objects.get(pano_id=message_dict['pano_id'])
        save_regions(message_dict, panorama)
        region_writer(panorama, google=True)
        panorama.status = Panorama.STATUS.detected_3
        panorama.save()

        log.warning("   Face3 done! %r" % message_dict['pano_id'])
