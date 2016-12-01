import logging

from django.core.management import BaseCommand

from datasets.shared.object_store import ObjectStore

object_store = ObjectStore()
log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        self._collect_test_detections(object_store.datapunt_conn, 'panorama', '/', '2016/04/')

    def _collect_test_detections(self, conn, container, delimiter, path):
        obj_name = path.split(delimiter)[-2]
        if 'cubic' in obj_name or 'equirect' in obj_name:
            return

        directory = object_store._get_full_container_list(conn, container, [],
                                                          delimiter=delimiter, prefix=path)
        subdirs = [store_object['subdir'] for store_object in directory if 'subdir' in store_object]
        subdirs.extend([file['name']+'/' for file in directory if 'name' in file and \
                        file['content_type'] == 'application/directory'])

        csvs = [file['name'] for file in directory if 'name' in file and file['name'][-4:] == '.csv']

        break_recursion = False
        for csv_file in csvs:
            if csv_file.endswith('no_regions_f.csv') or csv_file.endswith('no_regions_lp.csv'):
                self._process_no_regions_csv(csv_file)
                break_recursion = True
            elif csv_file.endswith('regions_f.csv') or csv_file.endswith('regions.csv'):
                self._process_f_regions_csv(csv_file)
                break_recursion = True
            elif  csv_file.endswith('regions_lp.csv'):
                self._process_lp_regions_csv(csv_file)
                break_recursion = True

        if break_recursion:
            return

        for subdir in subdirs:
            log.info('walking subdir: {}'.format(subdir))
            self._collect_test_detections(conn, container, delimiter, subdir)

    def _process_lp_regions_csv(self, csv_file):
        pass

    def _process_f_regions_csv(self, csv_file):
        pass

    def _process_no_regions_csv(self, csv_file):
        pass

