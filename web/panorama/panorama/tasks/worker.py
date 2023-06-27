import logging
import time

from django.db import connection, transaction

from datasets.panoramas.models import Panoramas, Region
from panorama.regions import blur, faces, license_plates
from panorama.tasks.detection import save_regions, region_writer
from panorama.tasks.utilities import reset_abandoned_work, call_for_close
from panorama.transform import equirectangular
from panorama.transform import utils_img_file as Img
from panorama.transform import utils_img_file_set as ImgSet
from panorama.transform.utils_img_file import save_array_image


log = logging.getLogger(__name__)


class _wait_for_panorama_table(object):
    def __enter__(self):
        while True:
            log.warning("waiting for panoramas table...")
            time.sleep(10)
            if self._panorama_table_present():
                log.warning("done waiting for panoramas table")
                break

    def __exit__(self, key, value, traceback):
        pass

    def _panorama_table_present(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select * from information_schema.tables where table_name=%s",
                    ("panoramas_panorama",),
                )
                return bool(cursor.rowcount)
        except Exception as e:
            log.error(e)
        return False


class Worker:
    def do_work(self):
        self.take_available_work()

        # Give other nodes time to finish
        time.sleep(600)

        # When running in the 100.000 tasks some fail (we're a bit too marginal on memory), reset status
        # and retry doing work on them
        reset_abandoned_work()
        self.take_available_work()

        # Notify Jenkins that job is done
        call_for_close()

        # back off of swarm when done (if this time = 0, each node will
        #   restart continuously when work is done)
        time.sleep(600)

    def take_available_work(self):
        with _wait_for_panorama_table():
            while self._still_work_to_do():
                # work is done in _still_work_to_do
                pass

    def _still_work_to_do(self):
        """
        The meat of the work is done in the process() method of the workers.
        That method returns true if there was a panorama to process for that stage.
        States are processed right to left (blurrer first), for maximum throughput
        """
        still_working = (
            RegionBlurrer().process() is True
            or AllRegionDetector().process() is True
            or PanoRenderer().process() is True
        )

        return still_working


class _PanoProcessor:
    status_queryset = None
    status_in_progress = None
    status_done = None

    def process(self):
        pano_to_process = self._get_next_pano()
        if not pano_to_process:
            return False

        self.process_one(pano_to_process)
        pano_to_process.status = self.status_done
        pano_to_process.save()

        return True

    def process_one(self, panorama):
        pass

    def _get_next_pano(self):
        try:
            with transaction.atomic():
                next_pano = self.status_queryset.select_for_update()[0]
                next_pano.status = self.status_in_progress
                next_pano.save()

            return next_pano
        except IndexError:
            return None


class RegionBlurrer(_PanoProcessor):
    status_queryset = Panoramas.detected
    status_in_progress = Panoramas.STATUS.blurring
    status_done = Panoramas.STATUS.done

    def process_one(self, panorama: Panoramas):
        im = Img.get_intermediate_panorama_image(panorama.get_intermediate_url())
        regions = [
            region.as_dict()
            for region in Region.objects.filter(pano_id=panorama.pano_id).all()
        ]

        if len(regions) > 0:
            im = blur.blur(im, regions)
        ImgSet.save_image_set(panorama.get_intermediate_url(), im)


class AllRegionDetector(_PanoProcessor):
    status_queryset = Panoramas.rendered
    status_in_progress = Panoramas.STATUS.detecting_regions
    status_done = Panoramas.STATUS.detected

    def process_one(self, panorama: Panoramas):
        start_time = time.time()
        im = Img.get_intermediate_panorama_image(panorama.get_intermediate_url())

        regions = license_plates.from_openalpr(im)
        self.save_regions(panorama, regions, start_time, lp=True)

        # detect faces 1
        start_time = time.time()
        face_detector = faces.FaceDetector(panorama.get_intermediate_url())
        face_detector.panorama_img = im

        regions = face_detector.get_opencv_face_regions()
        self.save_regions(panorama, regions, start_time)

        # detect faces 2
        start_time = time.time()
        regions = face_detector.get_dlib_face_regions()
        self.save_regions(panorama, regions, start_time, dlib=True)

        # detect faces 3
        start_time = time.time()
        regions = face_detector.get_vision_api_face_regions()
        self.save_regions(panorama, regions, start_time, google=True)

    def save_regions(self, panorama, regions, start_time, **kwargs):
        """Saves a CSV file containing the regions in db and object store."""
        for region in regions:
            millis = round((time.time() - start_time) * 1000)
            region[-1] += f", time={millis}ms"
        save_regions(regions, panorama, region_type="N")
        region_writer(panorama, **kwargs)


class PanoRenderer(_PanoProcessor):
    status_queryset = Panoramas.to_be_rendered
    status_in_progress = Panoramas.STATUS.rendering
    status_done = Panoramas.STATUS.rendered

    def process_one(self, pano: Panoramas):
        panorama_path = pano.path + pano.filename
        log.info(
            "START RENDERING panorama: {} in equirectangular projection.".format(
                panorama_path
            )
        )

        im = Img.get_raw_panorama_as_rgb_array(panorama_path)
        im = equirectangular.rotate(im, pano.heading, pano.pitch, pano.roll,
                target_width=8000)

        intermediate_path = "intermediate/{}".format(panorama_path)
        log.info("saving intermediate: {}".format(intermediate_path))

        save_array_image(im, intermediate_path, in_panorama_store=True)
