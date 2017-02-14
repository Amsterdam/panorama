"""
Batch import for the panorama dataset
"""

# Python
import csv
from datetime import datetime
import logging

# Package
from django.contrib.gis.geos import Point
from django.utils.timezone import utc as UTC_TZ

# Project
from datasets.panoramas.models import Panorama, Traject, EQUIRECTANGULAR_SUBPATH, FULL_IMAGE_NAME
from panorama.shared.object_store import ObjectStore

BATCH_SIZE = 50000
log = logging.getLogger(__name__)

# Conversion between GPS and UTC time
# Initial difference plus the 36 leap seconds recorded to date
# When a new leap second is introduced the import will need
# to change to accommodate for it
# or it can be ignored, assuming that
UTCfromGPS = 315964800 - 36


class ImportPanoramaJob(object):
    """
    Simple import script.
    It looks through the paths looking for metadata and
    trojectory files to import
    """
    files_in_panodir = []
    files_in_renderdir = []
    object_store = ObjectStore()

    def process(self):
        """
        Main import process
        The import is done type first instead of complete import of
        each mission.
        First all the panorama metadata files are imported,
        then all the trajectory
        files.
        """
        csvs = self.object_store.get_csvs('panorama')
        for csv_file in csvs:
            log.info('READING panorama: %s', csv_file['name'])
            container = csv_file['container']
            path = csv_file['name'].replace(csv_file['name'].split('/')[-1], '')
            self.files_in_panodir = [file['name'] for file in
                                     self.object_store.get_panorama_store_objects(container, path)]
            self.files_in_renderdir = [file['name'] for file in
                                       self.object_store.get_datapunt_store_objects(container + '/' + path)]
            Panorama.objects.bulk_create(
                self.process_csv(csv_file, self.process_panorama_row),
                batch_size=BATCH_SIZE
            )

        for csv_file in self.object_store.get_csvs('trajectory'):
            log.info('READING trajectory: %s', csv_file['name'])
            Traject.objects.bulk_create(
                self.process_csv(csv_file, self.process_traject_row),
                batch_size=BATCH_SIZE
            )

    def process_csv(self, csv_file, process_row_callback):
        """
        Process a single csv file
        """
        models = []

        csv_file_iterator = iter(self.object_store.get_panorama_store_object(csv_file).decode("utf-8").split('\n'))
        rows = csv.reader(csv_file_iterator,
                          delimiter='\t',
                          quotechar=None,
                          quoting=csv.QUOTE_NONE)
        headers = next(rows)
        path = csv_file['name'].replace(csv_file['name'].split('/')[-1], '')
        for row in rows:
            model_data = dict(zip(headers, row))
            model = process_row_callback(model_data, csv_file['container'], path)
            if model:
                models.append(model)
        return models

    def process_panorama_row(self, row, container, path):
        """
        Process a single row in the panorama photos metadata csv
        """
        try:
            base_filename = row['panorama_file_name']
        except KeyError:
            return None

        # check if pano file exists
        pano_image = base_filename + '.jpg'
        if path+pano_image not in self.files_in_panodir:
            log.error('MISSING Panorama: %s/%s/%s', container, path, pano_image)
            return None

        # check if rendered pano file exists
        rendered_image = base_filename + EQUIRECTANGULAR_SUBPATH + FULL_IMAGE_NAME
        is_pano_rendered = container+'/'+path+rendered_image in self.files_in_renderdir

        # Creating unique id from mission id and pano id
        pano_id = '%s_%s' % (path.split('/')[-2], base_filename)

        return Panorama(
            pano_id=pano_id,
            status=Panorama.STATUS.rendered if is_pano_rendered else Panorama.STATUS.to_be_rendered,
            timestamp=self._convert_gps_time(row['gps_seconds[s]']),
            filename=pano_image,
            path=container+'/'+path,
            geolocation=Point(
                float(row['longitude[deg]']),
                float(row['latitude[deg]']),
                float(row['altitude_ellipsoidal[m]'])
            ),
            roll=float(row['roll[deg]']),
            pitch=float(row['pitch[deg]']),
            heading=float(row['heading[deg]']),
        )

    def process_traject_row(self, row):
        """
        Process a single row in the trajectory csv file
        """
        if not row:
            return None

        return Traject(
            timestamp=self._convert_gps_time(row['gps_seconds[s]']),
            geolocation=Point(
                float(row['longitude[deg]']),
                float(row['latitude[deg]']),
                float(row['altitude_ellipsoidal[m]'])
            ),

            north_rms=float(row['north_rms[m]']),
            east_rms=float(row['east_rms[m]']),
            down_rms=float(row['down_rms[m]']),
            roll_rms=float(row['roll_rms[deg]']),
            pitch_rms=float(row['pitch_rms[deg]']),
            heading_rms=float(row['heading_rms[deg]']),
        )

    def _convert_gps_time(self, gps_time):
        """
        Converts the GPS time to unix timestamp
        Paramaters:
        - gps_time: gps time as timestamp
        - local: optional parmeter. wether to convert to utc
          or local time

        Returns:
        unix timestamp representing the date and time,
        either in utc or local time
        """
        gps_time = float(gps_time)
        # utcfromtimestamp sets the tzinfo to None,
        # which is kind of true but causes
        # a warning from django and may lead to bugs on
        # later code changes. Therefore
        # the timezone is manually set to utc.
        timestamp = datetime.utcfromtimestamp(
            gps_time + UTCfromGPS).replace(tzinfo=UTC_TZ)
        return timestamp
