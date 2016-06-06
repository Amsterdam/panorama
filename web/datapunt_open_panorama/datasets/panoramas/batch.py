"""
Basisinformatie maakt binnen een opnameseizoen dagelijks opnames.
Elke opnamedag worden er 'missies' aangemaakt.
Binnen een missie komen 1 of meerdere 'runs' voor. Een run is een
aaneengesloten opname van meerdere beelden.

Basisinformatie verwerkt de ruwe opnames en de ruwe navigatiegegevens,
en upload deze naar de bestandsserver van
Datapunt.

De mappenstructuur is `<panoserver>/YYYY/MM/DD/<missienaam>/`.

Bijvoorbeeld: `<panoserver>/2016/04/11/TMX7315120208-000027/`.

In elke map komen de volgende bestanden voor:
1. pano_<run>_<panorama-id>.jpg
2. panorama1.csv
3. trajectory.csv
4. Camera_xxxxxxxx_YYYYMMDD.sync
5. <missienaam>_xxxxxxx.log

Per dag / missie worden de volgende bestanden gegenereerd:
Ad 1)   de beelden zelf. Er is altijd 1 Run binnen een missie.
        De run-nummering begint bij 0. De panorama-id is een
        nulgebaseerd volgnummer binnen de run. Bijvoorbeeld:
        de tweede afbeelding binnen de 3e run heet: `pano_0002_000001.jpg`.
Ad 2)   opnamelocaties en metadata van de beelden
Ad 3)   metadata van het gereden traject,inclusief de kwaliteit van
        de navigatie.
Ad 4)   aanvullende informatie over de opnametijden
Ad 5)   procesinformatie van de missie, waaronder de missienaam

Op dit moment zijn de eerste 3 bestanden relevant.
De structuur van de twee csv-bestanden (2) en (3) wordt hieronder
toegelicht.

### panorama1.csv ###
Tab-gescheiden

Bevat de metadata van de opnames.

| kolomnaam                 | voorbeeld         | betekenis     |
|-------------------------- | ----------------- | --------------|
| `gps_seconds[s]`          | 1119865163.26577  | tijd          |
| `panorama_file_name`      | pano_0000_000000  | bestandsnaam  |
| `latitude[deg]`           | 52.3637434695634  | opnamelocatie |
| `longitude[deg]`          | 5.1860815788512   |               |
| `altitude_ellipsoidal[m]` | 42.3710962571204  |               |
| `roll[deg]`               | -2.04336774663454 | camerastand   |
| `pitch[deg]`              | 1.8571838859381   |               |
| `heading[deg]`            | 359.39712516717   |               |

### trajectory.csv ###
Tab-gescheiden

Bevat de metadata van het gereden traject, inclusief de kwaliteit
van de navigatie.
Deze gegevens zijn niet nodig om de opnamelocaties en de
beelden zelf te tonen, maar kunnen gebruikt worden als een
indicatie van waar gereden is, en als indicatie
van de navigatiekwaliteit.

| kolomnaam                 | voorbeeld          | betekenis     |
|-------------------------- | ------------------ | --------------|
| `gps_seconds[s]`          | 1119864909.00311	 | tijd          |
| `latitude[deg]`           | 52.3638859873144	 | locatie       |
| `longitude[deg]`          | 5.18583889988423	 |               |
| `altitude_ellipsoidal[m]` | 42.1257964957097	 |               |
| `north_rms[m]`            | 0.0337018163617934 | kwaliteit     |
| `east_rms[m]`	            | 0.0254896778492272 |               |
| `down_rms[m]`	            | 0.041721045361001	 |               |
| `roll_rms[deg]`           | 0.0294313546384066 |               |
| `pitch_rms[deg]`          | 0.0310816854803103 |               |
| `heading_rms[deg]`	    | 0.208372506807263	 |               |



"""
# Python
from contextlib import contextmanager
import csv
from datetime import datetime
import glob
import logging
import os
import os.path
import pytz
# Package
from django.contrib.gis.geos import Point
from django.conf import settings


from . import models

BATCH_SIZE = 50000


log = logging.getLogger(__name__)

# Conversion between GPS and UTC time
# Initial difference plus the 36 leap seconds recorded to date
# When a new leap second is introduced the import will need to change to accommodate for it
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


def process_csv(paths, process_row_callback):

    models = []

    for csvfilepath in paths:
        csv_path = str(csvfilepath[:-1], 'UTF-8')
        # cut off last csv file name
        relative_path = "/".join(csv_path.split('/')[:-1])
        full_path = "/".join([settings.BASE_DIR, csv_path])

        # parse the csv
        with _context_reader(full_path) as rows:

            for model_data in rows:
                model = process_row_callback(model_data, relative_path)
                if model:
                    models.append(model)

    return models


class ImportPanoramaJob(object):
    """
    Simple import script.
    Locate paths that have been modified since last import date.

    NOTE:

    WE ASUME ONLY NEW FILES/FOLDERS ARE ADDED
    and old files/folders are not changed

    WE do not notice DELETE's
    """

    def _get_last_pano_file(self):
        """
        Find the last added panorama and add it
        """

        last_pano = None

        if models.Panorama.objects.count():
            last_pano = models.Panorama.objects.latest(
                field_name='timestamp')

        msg = last_pano

        if not last_pano:
            msg = 'No old panoramas loaded'

        log.debug('Latest is: %s', msg)

        return last_pano

    def find_metadata_files(self, file_match, root_dir='panoramas'):
        """
        Finds the csv files containing the metadata

        Parameters:
        file_match - The file searhc pattern describing the file name
        root_dir - The starting point to for file searching

        Returns:
        A, potentailly empty, list of file names matching the search criteria
        """
        path = '%s/**/%s' % (root_dir, file_match)
        files = glob.glob(path, recursive=True)
        paths = output.stdout.readlines()
        return files

    def process(self):
        """
        Main import process
        The import is done type first instead of complete import of each mission.
        First all the panorama metadata files are imported, then all the trajectory
        files.
        """
        files = self.find_metadata_files('panorama*.csv')
        models.Panorama.objects.bulk_create(
            process_csv(files, self.process_panorama_row),
            batch_size=BATCH_SIZE
        )

        files = self.find_metadata_files('trajectory.csv')
        models.Traject.objects.bulk_create(
            process_csv(files, self.process_traject_row),
            batch_size=BATCH_SIZE
        )

        paths = self.find_new_paths(models.Panorama, 'pano*.jpg')

    def _get_valid_timestamp(self, row):
        t_gps = float(row['gps_seconds[s]'])
        timestamp = datetime.utcfromtimestamp(t_gps + GPSfromUTC)
        timestamp = pytz.utc.localize(timestamp)
        return timestamp

    def process_panorama_row(self, row, path):

        filename = row['panorama_file_name'] + '.jpg'
        file_path = os.path.join(settings.BASE_DIR, path, filename)

        # check if pano file exists
        if not os.path.isfile(file_path):
            log.error('MISSING Panorama: %s/%s', path, filename)
            return None

        return models.Panorama(
            timestamp=self._get_valid_timestamp(row),
            filename=filename,
            path=path,
            opnamelocatie=Point(
                float(row['latitude[deg]']),
                float(row['longitude[deg]']),
                float(row['altitude_ellipsoidal[m]'])
            ),
            roll=float(row['roll[deg]']),
            pitch=float(row['pitch[deg]']),
            heading=float(row['heading[deg]']),
        )

    def process_traject_row(self, row, path):

        return models.Traject(
            timestamp=self._get_valid_timestamp(row),
            opnamelocatie=Point(
                float(row['latitude[deg]']),
                float(row['longitude[deg]']),
                float(row['altitude_ellipsoidal[m]'])
            ),
            north_rms=float(row['north_rms[m]']),
            east_rms=float(row['east_rms[m]']),
            down_rms=float(row['down_rms[m]']),
            roll_rms=float(row['roll_rms[deg]']),
            pitch_rms=float(row['pitch_rms[deg]']),
            heading_rms=float(row['heading_rms[deg]']),
        )

    def create_thumbnails(self, panorama_list):
        """
        SHOULD BE DONE Dynamic based on directon
        location pano / view location
        """
        raise NotImplementedError()
        # STUFF FOR LATER
