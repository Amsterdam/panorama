import json, time
import logging
from random import randrange

from datapunt.management.queue import Worker
from datasets.panoramas.regions import license_plates
from . shared_util import save_detected_image

log = logging.getLogger(__name__)


class DetectLicensePlates(Worker):
    _route = 'license_plate_task'
    _route_out = 'license_plate_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        start_time = time.time()
        lp_detector = license_plates.LicensePlateDetector(message_dict['panorama_url'])

        regions = lp_detector.get_licenseplate_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        return [{'pano_id': message_dict['pano_id'],
                 'regions': regions}]

