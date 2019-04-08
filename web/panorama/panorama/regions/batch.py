import csv
import logging

from datasets.panoramas.models import Region
from datasets.panoramas.models import Panoramas
from panorama.shared.object_store import ObjectStore

BATCH_SIZE = 1000
log = logging.getLogger(__name__)


class ImportRegions(object):
    """
    Simple import script.
    It looks through the results-dir for regions. Expects panoramas in database
    Used for one-off (hopefully) restore of the given data.
    """
    object_store = ObjectStore()

    def process(self):
        regions = []
        for year in self.object_store.get_datapunt_subdirs('results/'):
            for month in self.object_store.get_datapunt_subdirs(year):
                for day in self.object_store.get_datapunt_subdirs(month):
                    csvs = self.object_store.get_detection_csvs(day)
                    for csv_file in csvs:
                        new_regions = self.process_detection_csvs(csv_file)
                        regions.extend(new_regions)
                        if len(regions) > 1000:
                            Region.objects.bulk_create(regions, batch_size=BATCH_SIZE)
                            regions = []

        Region.objects.bulk_create(regions, batch_size=BATCH_SIZE)

    def process_detection_csvs(self, csv_file):
        regions = []

        pano_id = '_'.join(csv_file['name'].split('/')[-3:-1])
        csv_file_iterator = iter(self.object_store.get_datapunt_store_object(csv_file['name'])
                                 .decode("utf-8")
                                 .split('\n'))
        rows = csv.reader(csv_file_iterator,
                          delimiter=',',
                          quotechar='"',
                          quoting=csv.QUOTE_MINIMAL)
        headers = next(rows)
        panorama = None
        for idx, row in enumerate(rows):
            if panorama is None:
                panorama = Panoramas.objects.get(pano_id=pano_id)
            model_data = dict(zip(headers, row))
            region = self.process_region_row(model_data, panorama)
            if region:
                regions.append(region)

        return regions

    def process_region_row(self, model_data, panorama: Panoramas):
        try:
            region_type = model_data['region_type']
        except KeyError:
            return None

        return Region(
            pano_id=panorama.pano_id,
            region_type=region_type,
            detected_by=model_data['detected_by'],

            left_top_x=model_data['left_top_x'],
            left_top_y=model_data['left_top_y'],
            right_top_x=model_data['right_top_x'],
            right_top_y=model_data['right_top_y'],
            right_bottom_x=model_data['right_bottom_x'],
            right_bottom_y=model_data['right_bottom_y'],
            left_bottom_x=model_data['left_bottom_x'],
            left_bottom_y=model_data['left_bottom_y']
        )
