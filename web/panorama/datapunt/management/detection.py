import csv
import logging
import io

from datasets.panoramas.models import Panorama, Region
from datasets.shared.object_store import ObjectStore

log = logging.getLogger(__name__)


def region_writer(panorama: Panorama, lp=False, dlib=False):
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
        csv_name = 'results/{}{}/regions_f{}.csv'.format(panorama.path, panorama.filename[:-4], 'd' if dlib else '')
    log.warn('saving {}'.format(csv_name))

    object_store.put_into_datapunt_store(csv_name, output.getvalue(), 'text/csv')


def save_regions(message_dict, panorama, region_type='G'):
    for region in message_dict['regions']:
        rg = Region()

        rg.panorama = panorama
        rg.region_type = region_type
        rg.detected_by = region[-1]

        left_top, right_top, right_bottom, left_bottom = region[0:4]

        rg.left_top_x = left_top[0]
        rg.left_top_y = left_top[1]
        rg.right_top_x = right_top[0]
        rg.right_top_y = right_top[1]
        rg.right_bottom_x = right_bottom[0]
        rg.right_bottom_y = right_bottom[1]
        rg.left_bottom_x = left_bottom[0]
        rg.left_bottom_y = left_bottom[1]

        rg.save()
