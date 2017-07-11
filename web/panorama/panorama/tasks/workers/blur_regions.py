import logging

from datasets.panoramas.models import Panorama, Region
from panorama.regions import blur
from panorama.transform import utils_img_file_set as ImgSet
from .pano_processor import PanoProcessor

log = logging.getLogger(__name__)


class RegionBlurrer(PanoProcessor):
    status_queryset = Panorama.detected_3
    status_in_progress = Panorama.STATUS.blurring
    status_done = Panorama.STATUS.done

    def process_one(self, panorama: Panorama):
        region_blurrer = blur.RegionBlurrer(panorama.get_intermediate_url())
        regions = []
        for region in Region.objects.filter(pano_id=panorama.pano_id).all():
            regions.append(blur.dict_from(region))

        if len(regions) > 0:
            ImgSet.save_image_set(panorama.get_intermediate_url(), region_blurrer.get_blurred_image(regions))
        else:
            ImgSet.save_image_set(panorama.get_intermediate_url(), region_blurrer.get_unblurred_image())
