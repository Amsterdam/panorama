from django.core.management.base import BaseCommand, CommandError
from datasets.panoramas.models import Panorama, Region
from panorama.regions.blur import dict_from, RegionBlurrer
from panorama.transform import utils_img_file_set as ImgSet


class Command(BaseCommand):
    help = "Blur pano (do provide pano_id): ./manage.py blur_pano --pano_id TMX7316060226-000030_pano_0008_000650"

    def add_arguments(self, parser):
        parser.add_argument('--pano_id', required=True)

    def handle(self, *args, **options):
        if 'pano_id' not in options:
            self.stderr.write("argument --pano_id is verplicht")
            self.stdout.write(self.help)
            return

        pano_id = options['pano_id']
        pano = Panorama.objects.filter(pano_id=pano_id).all()[0]

        if pano:
            pano_path = pano.path+pano.filename

            regions = []
            for region in Region.objects.filter(pano_id=pano_id).all():
                regions.append(dict_from(region))

            region_blurrer = RegionBlurrer(pano_path)
            blurred_image = region_blurrer.get_blurred_image(regions)

            ImgSet.save_image_set(pano_path, blurred_image)
