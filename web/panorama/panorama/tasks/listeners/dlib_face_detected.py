import logging
import json

from panorama.tasks.queue import BaseListener
from panorama.tasks.detection import save_regions, region_writer
from datasets.panoramas.models import Panorama

log = logging.getLogger(__name__)


class FaceDone(BaseListener):
    _route = 'face2_done'

    def on_message(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        panorama = Panorama.objects.get(pano_id=message_dict['pano_id'])
        save_regions(message_dict, panorama)
        region_writer(panorama, dlib=True)
        panorama.status = Panorama.STATUS.detected_2
        panorama.save()

        log.warning("   Face2 done! %r" % message_dict['pano_id'])
