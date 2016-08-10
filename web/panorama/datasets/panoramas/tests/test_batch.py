from unittest import mock
import glob

from django.test import TransactionTestCase

from ..batch import ImportPanoramaJob
from ..models import Panorama, Traject


def mock_get_csvs(csv_type):
    files = []
    if csv_type == 'panorama':
        files = glob.glob('/app/panoramas_test/**/panorama*.csv', recursive=True)
    if csv_type == 'trajectory':
        files = glob.glob('/app/panoramas_test/**/trajectory.csv', recursive=True)
    return [{'container': '1', 'name': f} for f in files]

def mock_pano_objs(container, path):
    return [{'name': f} for f in glob.glob(path+'*.jpg')]

def mock_dp_objs(path):
    return [{'name': f} for f in glob.glob(path[2:]+'*.jpg')]

def mock_get_csv(csv):
    with open(csv['name'], mode='rb') as file:
        return file.read()

mock_objs = 'datasets.panoramas.batch.ImportPanoramaJob.object_store.%s'


class ImportPanoTest(TransactionTestCase):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas_test folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test datasets.panoramas.tests
    """

    @mock.patch(mock_objs % 'get_csvs', side_effect=mock_get_csvs)
    @mock.patch(mock_objs % 'get_panorama_store_objects', side_effect=mock_pano_objs)
    @mock.patch(mock_objs % 'get_datapunt_store_objects', side_effect=mock_dp_objs)
    @mock.patch(mock_objs % 'get_panorama_store_object', side_effect=mock_get_csv)
    def test_import(self, mock_1, mock_2, mock_3, mock_4):
        ImportPanoramaJob().process()

        panos = Panorama.objects.all()
        self.assertEqual(panos.count(), 14)

        trajecten = Traject.objects.all()
        self.assertEqual(trajecten.count(), 14)
