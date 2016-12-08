import csv
import logging
import io

from datasets.panoramas.models import Panorama, Region
from datasets.shared.object_store import ObjectStore

log = logging.getLogger(__name__)


def region_writer(panorama: Panorama, lp=False):
    object_store = ObjectStore()
    output = io.StringIO()
    writer = csv.writer(output)

    regions = Region.objects.filter(panorama=panorama)
    writer.writerow(['region_type', 'left_top_x', 'left_top_y', 'right_top_x', 'right_top_y', 'right_bottom_x',
                     'right_bottom_y', 'left_bottom_x', 'left_bottom_y', 'detected_by'])
    for region in regions:
        writer.writerow([region.region_type, region.left_top_x, region.left_top_y, region.right_top_x,
                         region.right_top_y, region.right_bottom_x, region.right_bottom_y, region.left_bottom_x,
                         region.left_bottom_y, region.detected_by])

    if lp:
        csv_name = 'results/{}{}/regions_lp.csv'.format(panorama.path, panorama.filename[:-4])
    else:
        csv_name = 'results/{}{}/regions_f.csv'.format(panorama.path, panorama.filename[:-4])
    log.warn('saving {}'.format(csv_name))

    object_store.put_into_datapunt_store(csv_name, output.getvalue(), 'text/csv')
