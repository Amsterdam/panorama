"""
Basisinformatie maakt binnen een opnameseizoen dagelijks opnames. Elke opnamedag worden er 'missies' aangemaakt.
Binnen een missie komen 1 of meerdere 'runs' voor. Een run is een aaneengesloten opname van meerdere beelden.

Basisinformatie verwerkt de ruwe opnames en de ruwe navigatiegegevens, en upload deze naar de bestandsserver van
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
Ad 1)   de beelden zelf. Er is altijd 1 Run binnen een missie. De run-nummering begint bij 0. De panorama-id is een
        nulgebaseerd volgnummer binnen de run. Bijvoorbeeld: de tweede afbeelding binnen de 3e run heet:
        `pano_0002_000001.jpg`.
Ad 2)   opnamelocaties en metadata van de beelden
Ad 3)   metadata van het gereden traject,inclusief de kwaliteit van de navigatie.
Ad 4)   aanvullende informatie over de opnametijden
Ad 5)   procesinformatie van de missie, waaronder de missienaam

Op dit moment zijn de eerste 3 bestanden relevant. De structuur van de twee csv-bestanden (2) en (3) wordt hieronder
toegelicht.

### panorama1.csv ###
Tab-gescheiden

Bevat de metadata van de opnames.

| kolomnaam                 | voorbeeld         | betekenis     |
|-------------------------- | ----------------- | --------------|
| `gps_seconds[s]`          | 1119865163.26577  | tijd          |
| `panorama_file_name`      | pano_0000_000000  | bestandsnaam  |
| `latitude[deg]`	        | 52.3637434695634  | opnamelocatie |
| `longitude[deg]`	        | 5.1860815788512   |               |
| `altitude_ellipsoidal[m]` | 42.3710962571204  |               |
| `roll[deg]`               | -2.04336774663454 | camerastand   |
| `pitch[deg]`              | 1.8571838859381   |               |
| `heading[deg]`            | 359.39712516717   |	            |

### trajectory.csv ###
Tab-gescheiden

Bevat de metadata van het gereden traject, inclusief de kwaliteit van de navigatie.
Deze gegevens zijn niet nodig om de opnamelocaties en de beelden zelf te tonen, maar kunnen gebruikt worden als een
indicatie van waar gereden is, en als indicatie van de navigatiekwaliteit.

| kolomnaam                 | voorbeeld          | betekenis     |
|-------------------------- | ------------------ | --------------|
| `gps_seconds[s]`	        | 1119864909.00311	 | tijd          |
| `latitude[deg]`	        | 52.3638859873144	 | locatie       |
| `longitude[deg]`	        | 5.18583889988423	 |               |
| `altitude_ellipsoidal[m]` | 42.1257964957097	 |               |
| `north_rms[m]`	        | 0.0337018163617934 | kwaliteit     |
| `east_rms[m]`	            | 0.0254896778492272 |               |
| `down_rms[m]`	            | 0.041721045361001	 |               |
| `roll_rms[deg]`	        | 0.0294313546384066 |               |
| `pitch_rms[deg]`	        | 0.0310816854803103 |               |
| `heading_rms[deg]`	    | 0.208372506807263	 |               |

"""

from contextlib import contextmanager
import csv
import os

from django.contrib.gis.db import models as geo

from . import models

BATCH_SIZE = 50000


def _wrap_row(r, headers):
    return dict(zip(headers, r))


@contextmanager
def _context_reader(source):
    if not os.path.exists(source):
        raise ValueError("File not found: {}".format(source))

    with open(source, encoding='cp1252') as f:
        rows = csv.reader(f, delimiter='\t', quotechar=None, quoting=csv.QUOTE_NONE)

        headers = next(rows)

        yield (_wrap_row(r, headers) for r in rows)


def process_csv(paths, process_row_callback):
    models = []

    for path in paths:
        with _context_reader(path) as rows:
            models += [result for result in (process_row_callback(r, path) for r in rows) if result]

    return models


class Import(object):
    panorama_paths = []
    trajectory_paths = []

    def find_new_paths(self):
        # TODO locate paths that have been changed based on last import date (sort model on timestamp?)
        return []

    def process(self):
        self.find_new_paths()

        models.Panorama.objects.bulk_create(
            process_csv(self.panorama_paths, self.process_panorama_row),
            batch_size=BATCH_SIZE
        )

        models.Traject.objects.bulk_create(
            process_csv(self.trajectory_paths, self.process_traject_row),
            batch_size=BATCH_SIZE
        )

    def process_panorama_row(self, row, path):
        return models.Panorama(
            timestamp=row['gps_seconds[s]'],
            filename=row['panorama_file_name'],
            path=path,
            opnamelocatie=geo.PointField(
                row['latitude[deg]'],
                row['longitude[deg]'],
                row['altitude_ellipsoidal[m]']
            ),
            roll=float(row['roll[deg]']),
            pitch=float(row['pitch[deg]']),
            heading=float(row['heading[deg]']),
        )

    def process_traject_row(self, row):
        return models.Traject(
            timestamp=row['gps_seconds[s]'],
            opnamelocatie=geo.PointField(
                row['latitude[deg]'],
                row['longitude[deg]'],
                row['altitude_ellipsoidal[m]']
            ),
            north_rms=float(row['north_rms[deg]']),
            east_rms=float(row['east_rms[deg]']),
            down_rms=float(row['down_rms[deg]']),
            roll_rms=float(row['roll_rms[deg]']),
            pitch_rms=float(row['pitch_rms[deg]']),
            heading_rms=float(row['heading_rms[deg]']),
        )

    def create_thumbnails(self):
        raise NotImplementedError
