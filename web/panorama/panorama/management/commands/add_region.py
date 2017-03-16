from django.core.management.base import BaseCommand, CommandError
from datasets.panoramas.models import Panorama, Region


class Command(BaseCommand):
    help = """
    Add a detected region to a panorama. Use as follows:

        ./manage.py add_region --pano_id <pano_id> --type <region-type G or N for face or licenseplate)> \
                               --coords <coordinates: left top x, y, right bottom x, y - no spaces>

    Example

        ./manage.py add_region --pano-id TMX7316060226-000030_pano_0008_000650 --type G --coords 1250,1990,1280,2010
    """

    def add_arguments(self, parser):
        parser.add_argument('--pano_id', required=True)
        parser.add_argument('--type', required=True)
        parser.add_argument('--coords', required=True)

    def handle(self, *args, **options):
        coords = options['coords'].split(',')
        region = Region(
            pano_id=options['pano_id'],
            region_type=options['type'],
            detected_by='manual',

            left_top_x=coords[0],
            left_top_y=coords[1],
            right_top_x=coords[2],
            right_top_y=coords[1],
            right_bottom_x=coords[2],
            right_bottom_y=coords[3],
            left_bottom_x=coords[0],
            left_bottom_y=coords[3]
        )
        region.save()

