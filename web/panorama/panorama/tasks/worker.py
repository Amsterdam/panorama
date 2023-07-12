import logging
import time

from django.db import connection, transaction

from datasets.panoramas.models import Panorama
from panorama.regions import blur, faces, license_plates
from panorama.tasks.detection import save_region_csv
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


def run():
    take_available_work()

    # Give other nodes time to finish
    time.sleep(600)

    # When running in the 100.000 tasks some fail (we're a bit too marginal on memory), reset status
    # and retry doing work on them
    #reset_abandoned_work()
    take_available_work()

    # back off of swarm when done (if this time = 0, each node will
    #   restart continuously when work is done)
    time.sleep(600)


def take_available_work():
    with _wait_for_panorama_table():
        # The meat of the work is done in the process() method of the workers.
        # That method returns true if there was a panorama to process for its
        # stage. States are processed right to left (blurrer first), for
        # maximum throughput.
        while RegionBlurrer().process() or PanoRenderer().process():
            pass


def reset_abandoned_work():
    with transaction.atomic():
        Panorama.blurring.all().update(status=Panorama.STATUS.detected)
        Panorama.detecting_regions.all().update(status=Panorama.STATUS.rendered)
        Panorama.rendering.all().update(status=Panorama.STATUS.to_be_rendered)


class _PanoProcessor:
    status_queryset = None
    status_in_progress = None
    status_done = None

    def process(self):
        pano_to_process = self._get_next_pano()
        if not pano_to_process:
            return False

        try:
            self.process_one(pano_to_process)
        except Exception as e:
            log.warning(e)
            _write_exception(pano_to_process, e)
            pano_to_process.status = Panorama.STATUS.error
        else:
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
    status_queryset = Panorama.rendered
    status_in_progress = Panorama.STATUS.blurring
    status_done = Panorama.STATUS.done

    def process_one(self, panorama: Panorama):
        start_time = time.time()
        url = panorama.get_intermediate_url()
        im = Img.get_intermediate_panorama_image(url)

        regions = license_plates.from_openalpr(im)
        self.save_regions(panorama, regions, start_time, "lp")

        all_regions = regions

        # detect faces 1
        start_time = time.time()
        regions = faces.from_opencv(im)
        self.save_regions(panorama, regions, start_time, "f")

        all_regions += regions

        # detect faces 2
        start_time = time.time()
        regions = faces.get_dlib_face_regions()
        self.save_regions(panorama, regions, start_time, "fd")

        all_regions += regions

        # detect faces 3
        start_time = time.time()
        regions = faces.from_google(im)
        self.save_regions(panorama, regions, start_time, "fg")

        all_regions += regions

        # Blur any regions found.
        if all_regions:
            im = blur.blur(im, all_regions)

        for path, im in ImgSet.make_equirectangular(url, im):
            Img.save_image(im, path)
        for path, im in ImgSet.make_cubic(url, im):
            Img.save_image(im, path)

    def save_regions(self, panorama, regions, start_time, suffix: str):
        """Saves a CSV file containing the regions in db and object store."""
        for region in regions:
            millis = round((time.time() - start_time) * 1000)
            region[-1] += f", time={millis}ms"
        save_region_csv(panorama, regions, suffix)


class PanoRenderer(_PanoProcessor):
    status_queryset = Panorama.to_be_rendered
    status_in_progress = Panorama.STATUS.rendering
    status_done = Panorama.STATUS.rendered

    def process_one(self, pano: Panorama):
        panorama_path = pano.path + pano.filename
        log.info(
            "START RENDERING panorama: {} in equirectangular projection.".format(
                panorama_path
            )
        )

        im = Img.get_raw_panorama_as_rgb_array(panorama_path)
        im = equirectangular.rotate(
            im, pano.heading, pano.pitch, pano.roll, target_width=8000
        )

        intermediate_path = "intermediate/{}".format(panorama_path)
        log.info("saving intermediate: {}".format(intermediate_path))

        save_array_image(im, intermediate_path, in_panorama_store=True)


def _write_exception(panorama, exc):
    objs = ObjectStore()
    log.info("saving exception")
    path = f"results/{panorama.path}{panorama.filename[:-4]}/error.txt"
    objs.put_into_datapunt_store(path, repr(exc), "text/plain")
