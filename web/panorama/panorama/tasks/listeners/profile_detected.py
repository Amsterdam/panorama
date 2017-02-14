import logging
import json

from panorama.tasks.queue import Listener
from panorama.tasks.detection import save_regions, region_writer
from datasets.panoramas.models import Panorama

log = logging.getLogger(__name__)


class ProfileDone(Listener):
    _route = 'profile_done'

    def on_message(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        panorama = Panorama.objects.get(pano_id=message_dict['pano_id'])
        save_regions(message_dict, panorama)
        region_writer(panorama, profile=True)
        panorama.status = Panorama.STATUS.detected_profile
        panorama.save()

        log.warning("   Face Profile! %r" % message_dict['pano_id'])
