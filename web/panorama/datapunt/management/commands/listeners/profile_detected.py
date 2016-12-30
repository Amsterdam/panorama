import logging
import json

from datapunt.management.queue import Listener
from datasets.panoramas.models import Panorama
from datapunt.management.detection import save_regions, region_writer

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
