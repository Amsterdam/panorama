import logging
import json

from datapunt.management.queue import Listener
from datapunt.management.detection import save_regions, region_writer
from datasets.panoramas.models import Panorama

log = logging.getLogger(__name__)


class LicensePlateDone(Listener):
    _route = 'license_plate_done'

    def on_message(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        panorama = Panorama.objects.get(pano_id=message_dict['pano_id'])
        save_regions(message_dict, panorama, region_type='N')
        region_writer(panorama, lp=True)
        panorama.status = Panorama.STATUS.detected_lp
        panorama.save()

        log.warning("     Licenseplate done! %r" % message_dict['pano_id'])
