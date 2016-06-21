"""
Batch import for the panorama dataset
"""

# Python
from contextlib import contextmanager
import csv
from datetime import datetime
import glob
import logging
import os
import os.path

# Package
from django.contrib.gis.geos import Point
from django.conf import settings
from django.utils.timezone import utc as UTC_TZ

# Project
from . import models

BATCH_SIZE = 50000


log = logging.getLogger(__name__)

# Conversion between GPS and UTC time
# Initial difference plus the 36 leap seconds recorded to date
# When a new leap second is introduced the import will need
# to change to accommodate for it
# or it can be ignored, assuming that
UTCfromGPS = 315964800 - 36


def _wrap_row(r, headers):
    return dict(zip(headers, r))


@contextmanager
def _context_reader(source):
    if not os.path.exists(source):
        raise ValueError("File not found: {}".format(source))

    with open(source, encoding='cp1252') as f:
        rows = csv.reader(
            f, delimiter='\t', quotechar=None, quoting=csv.QUOTE_NONE)

        headers = next(rows)

        yield (_wrap_row(r, headers) for r in rows)


class ImportPanoramaJob(object):
    """
    Simple import script.
    It looks through the paths looking for metadata and
    trojectory files to import
    """

    def find_metadata_files(self, file_match):
        """
        Finds the csv files containing the metadata

        Parameters:
        file_match - The file search pattern describing the file name
        root_dir - The starting point to for file searching

        Returns:
        A, potentailly empty, list of file names matching the search criteria
        """
        path = '%s/**/%s' % (settings.PANO_DIR, file_match)
        files = glob.glob(path, recursive=True)
        return files

    def process(self):
        """
        Main import process
        The import is done type first instead of complete import of
        each mission.
        First all the panorama metadata files are imported,
        then all the trajectory
        files.
        """
        files = self.find_metadata_files('panorama*.csv')
        models.Panorama.objects.bulk_create(
            self.process_csv(files, self.process_panorama_row),
            batch_size=BATCH_SIZE
        )

        files = self.find_metadata_files('trajectory.csv')
        models.Traject.objects.bulk_create(
            self.process_csv(files, self.process_traject_row),
            batch_size=BATCH_SIZE
        )

    def process_csv(self, files, process_row_callback):
        """
        Process a single csv file
        """
        models = []

        for csv_file in files:
            # parse the csv
            with _context_reader(csv_file) as rows:
                path = os.path.dirname(csv_file)
                for model_data in rows:
                    model = process_row_callback(model_data, path)
                    if model:
                        models.append(model)
        return models

    def process_panorama_row(self, row, path):
        """
        Process a single row in the panorama photos metadata csv
        """
        filename = row['panorama_file_name'] + '.jpg'
        file_path = os.path.join(settings.BASE_DIR, path, filename)
        # Creating unique id from mission id and pano id
        pano_id = '%s_%s' % (path.split('/')[-1], row['panorama_file_name'])
        # check if pano file exists
        if not os.path.isfile(file_path):
            log.error('MISSING Panorama: %s/%s', path, filename)
            return None

        return models.Panorama(
            pano_id=pano_id,
            timestamp=self._convert_gps_time(row['gps_seconds[s]']),
            filename=filename,
            path=path,
            geolocation=Point(
                float(row['longitude[deg]']),
                float(row['latitude[deg]']),
                float(row['altitude_ellipsoidal[m]'])
            ),

            geolocation2D=Point(
                float(row['longitude[deg]']),
                float(row['latitude[deg]']),
            ),

            roll=float(row['roll[deg]']),
            pitch=float(row['pitch[deg]']),
            heading=float(row['heading[deg]']),
        )

    def process_traject_row(self, row, path):
        """
        Process a single row in the trajectory csv file
        """
        return models.Traject(
            timestamp=self._convert_gps_time(row['gps_seconds[s]']),
            geolocation=Point(
                float(row['longitude[deg]']),
                float(row['latitude[deg]']),
                float(row['altitude_ellipsoidal[m]'])
            ),

            geolocation2D=Point(
                float(row['longitude[deg]']),
                float(row['latitude[deg]']),
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

    def create_thumbnails(self, panorama_list):
        """
        SHOULD BE DONE Dynamic based on directon
        location pano / view location
        """
        raise NotImplementedError()
        # STUFF FOR LATER
