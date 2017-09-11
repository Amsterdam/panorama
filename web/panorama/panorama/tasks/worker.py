# Python
import logging
import time

from panorama.tasks.mixins import PanoramaTableAware
from panorama.tasks.workers.render_pano import PanoRenderer
from panorama.tasks.workers.detect_lps import LicensePlateDetector
from panorama.tasks.workers.detect_faces import OpenCVFaceDetector
from panorama.tasks.workers.detect_faces_dlib import DlibFaceDetector
from panorama.tasks.workers.detect_faces_google import GoogleFaceDetector
from panorama.tasks.workers.blur_regions import RegionBlurrer

log = logging.getLogger(__name__)


class Worker(PanoramaTableAware):
    def do_work(self):
        with self.panorama_table_present():
            PanoRenderer().process_all()
            LicensePlateDetector().process_all()
            OpenCVFaceDetector().process_all()
            DlibFaceDetector().process_all()
            GoogleFaceDetector().process_all()
            RegionBlurrer().process_all()

        # back off of swarm
        time.sleep(1200)