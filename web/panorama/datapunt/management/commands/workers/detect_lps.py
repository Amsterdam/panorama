import json, time
from random import randrange

from datapunt.management.queue import Worker
from datasets.panoramas.regions import license_plates


class DetectLicensePlates(Worker):
    _route = 'license_plate_task'
    _route_out = 'license_plate_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        lp_detector = license_plates.LicensePlateDetector(message_dict['panorama_url'])
        regions = lp_detector.get_licenseplate_regions()

        return [{'pano_id': message_dict['pano_id'],
                 'regtions': regions}]
