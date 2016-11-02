import io

from PIL import Image
from django.conf import settings

from datasets.panoramas.models import Panorama
from datasets.shared.object_store import ObjectStore
from . transformer import PANO_FOV, PANO_HORIZON, PANO_ASPECT

object_store = ObjectStore()


class Thumbnail:
    def __init__(self, panorama:Panorama):
        self.panorama = panorama

    def get_image(self, target_width=750, target_fov=80, target_horizon=0.3, target_heading=0, target_aspect=1.5):
        source_image, source_width = self._choose_source_image_and_width(target_fov, target_width)
        source_height = int(source_width/PANO_ASPECT)

        crop = self._calculate_crop(source_width, target_fov, target_aspect, target_heading, target_horizon)
        img_url = self.panorama.equirectangular_img_urls[source_image].replace(settings.PANO_IMAGE_URL+'/', '')
        full_img = Image.open(io.BytesIO(object_store.get_datapunt_store_object(img_url)))

        wrap_around = Image.new('RGB', (2*source_width, source_height))
        wrap_around.paste(full_img, (0, 0, source_width, source_height))
        wrap_around.paste(full_img, (source_width, 0, 2*source_width, source_height))
        
        crop_img = wrap_around.crop(crop)
        return crop_img.resize((target_width, int(target_width/target_aspect)), Image.BICUBIC)

    def _calculate_crop(self, source_width, target_fov, target_aspect, target_heading, target_horizon):
        target_center = source_width / 2 + target_heading * source_width / 360
        chunk_width = source_width * target_fov / PANO_FOV
        chunk_height = chunk_width / target_aspect
        chunk_above_horizon = chunk_height * (1 - target_horizon)

        left = target_center - chunk_width / 2
        top = (1 - PANO_HORIZON) * source_width / PANO_ASPECT - chunk_above_horizon
        right = left + chunk_width
        bottom = top + chunk_height

        return int(left), int(top), int(right), int(bottom)

    def _choose_source_image_and_width(self, target_fov, target_width):
        pixels_per_degree = target_width / target_fov
        if pixels_per_degree > 4000 / 360:
            return 'full', 8000
        elif pixels_per_degree > 2000 / 360:
            return 'medium', 4000
        return 'small', 2000
