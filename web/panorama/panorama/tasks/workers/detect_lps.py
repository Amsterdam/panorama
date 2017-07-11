import logging
import time

from datasets.panoramas.models import Panorama
from panorama.regions import license_plates
from panorama.tasks.detection import save_regions, region_writer
from .pano_processor import PanoProcessor

log = logging.getLogger(__name__)


class LicensePlateDetector(PanoProcessor):
    status_queryset = Panorama.rendered
    status_in_progress = Panorama.STATUS.detecting_lp
    status_done = Panorama.STATUS.detected_lp

    def process_one(self, panorama: Panorama):
        start_time = time.time()
        lp_detector = license_plates.LicensePlateDetector(panorama.get_intermediate_url())

        regions = lp_detector.get_licenseplate_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        save_regions(regions, panorama, region_type='N')
        region_writer(panorama, lp=True)
