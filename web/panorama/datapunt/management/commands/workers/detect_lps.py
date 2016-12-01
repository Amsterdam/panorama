import json, time
import logging
from random import randrange

from datapunt.management.queue import Worker
from datasets.panoramas.regions import license_plates
from . shared_util import save_detected_image


ZOOM_RANGE = [1, 1.08, 1.175, 1.29, 1.41]

log = logging.getLogger(__name__)


class DetectLicensePlates(Worker):
    _route = 'license_plate_task'
    _route_out = 'license_plate_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        rand_zoom = randrange(len(ZOOM_RANGE))
        rand_shear = randrange(2, 8)

        license_plates.ANGLE_RANGE = range(rand_shear, 10*rand_shear+1, rand_shear)
        license_plates.ZOOM_RANGE = [ZOOM_RANGE[rand_zoom]]

        start_time = time.time()
        lp_detector = license_plates.LicensePlateDetector(message_dict['panorama_url'])
        regions = lp_detector.get_licenseplate_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        detected_by = "shear_angle={}, zoom={}, time={}ms" \
            .format(rand_shear, ZOOM_RANGE[rand_zoom], int(round((time.time() - start_time) * 1000)))

        full_image = lp_detector.panorama_img
        pano_id = "_".join(message_dict['panorama_url'].split('/')[-4:-2])
        target_file = 'detection_test/lp/{}/{}/{}.jpg'.format(ZOOM_RANGE[rand_zoom], rand_shear, pano_id)

        log.info('    saving {}'.format(target_file))
        save_detected_image(full_image, regions, target_file)


        return [{'pano_id': message_dict['pano_id'],
                 'regions': regions,
                 'detected_by': detected_by}]

