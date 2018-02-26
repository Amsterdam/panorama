import logging
import time

from datasets.panoramas.models import Panorama
from panorama.regions import license_plates
from panorama.regions import faces
from panorama.tasks.detection import save_regions, region_writer
from .pano_processor import PanoProcessor

log = logging.getLogger(__name__)


class AllRegionDetector(PanoProcessor):
    status_queryset = Panorama.rendered
    status_in_progress = Panorama.STATUS.detecting_lp
    status_done = Panorama.STATUS.detected_3

    def process_one(self, panorama: Panorama):
        start_time = time.time()
        lp_detector = license_plates.LicensePlateDetector(panorama.get_intermediate_url())

        regions = lp_detector.get_licenseplate_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        save_regions(regions, panorama, region_type='N')
        region_writer(panorama, lp=True)

        # detect faces 1
        start_time = time.time()
        face_detector = faces.FaceDetector(panorama.get_intermediate_url())
        face_detector.panorama_img = lp_detector.panorama_img

        regions = face_detector.get_opencv_face_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        save_regions(regions, panorama)
        region_writer(panorama)

        # detect faces 2
        start_time = time.time()
        regions = face_detector.get_dlib_face_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        save_regions(regions, panorama)
        region_writer(panorama, dlib=True)

        # detect faces 3
        start_time = time.time()
        regions = face_detector.get_vision_api_face_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        save_regions(regions, panorama)
        region_writer(panorama, google=True)
