import glob
import logging
import os
from django.test import TransactionTestCase
from unittest import mock, skipIf

from datasets.panoramas.models import Panorama, Traject, Mission, RecentPanorama
from panorama.batch import ImportPanoramaJob
from panorama.management.commands.refresh_views import Command as RefreshCommand

log = logging.getLogger(__name__)


def mock_get_csvs(csv_type):
    files = []
    if csv_type == 'panorama':
        files = glob.glob('/app/panoramas_test/**/panorama*.csv', recursive=True)
    if csv_type == 'trajectory':
        files = glob.glob('/app/panoramas_test/**/trajectory.csv', recursive=True)
    return [{'container': '1', 'name': f} for f in files]


def mock_get_root_csvs(csv_type):
    files = []
    if csv_type == 'missiegegevens':
        files = glob.glob('/app/panoramas_test/**/missiegegevens.csv', recursive=True)
    return [{'container': '1', 'name': f} for f in files]


def mock_pano_objectstore(container, path):
    return [{'name': f} for f in glob.glob(path+'*.jpg')]


def mock_dp_objectstore(path):
    return [{'name': f} for f in glob.glob(path[2:]+'*.jpg')]


def mock_get_csv(csv):
    with open(csv['name'], mode='rb') as file:
        return file.read()

mock_objectstore = 'panorama.batch.ImportPanoramaJob.object_store.%s'


@skipIf(not os.path.exists('/app/panoramas_test'),
        'Import test skipped: no mounted directory found, run in docker container')
class ImportPanoTest(TransactionTestCase):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas_test folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test panorama.tests.test_batch
    """
    allow_database_queries = True

    @mock.patch(mock_objectstore % 'get_csvs', side_effect=mock_get_csvs)
    @mock.patch(mock_objectstore % 'get_containerroot_csvs', side_effect=mock_get_root_csvs)
    @mock.patch(mock_objectstore % 'get_panorama_store_objects', side_effect=mock_pano_objectstore)
    @mock.patch(mock_objectstore % 'get_datapunt_store_objects', side_effect=mock_dp_objectstore)
    @mock.patch(mock_objectstore % 'get_panorama_store_object', side_effect=mock_get_csv)
    def test_import(self, *args):
        ImportPanoramaJob().process()
        for pano in Panorama.objects.all():
            pano.status = Panorama.STATUS.done
            pano.save()

        RefreshCommand().refresh_views()

        missies = Mission.objects.all()
        self.assertEqual(missies.count(), 11)

        self.assertEqual(Mission.objects.filter(neighbourhood='AUTOMATICALLY CREATED').count(), 2)
        self.assertEqual(Mission.objects.filter(surface_type='L').count(), 7)
        self.assertEqual(Mission.objects.filter(surface_type='W').count(), 4)
        self.assertEqual(Mission.objects.filter(mission_distance=5).count(), 7)
        self.assertEqual(Mission.objects.filter(mission_distance=10).count(), 4)
        self.assertEqual(Mission.objects.filter(mission_type='bi').count(), 8)
        self.assertEqual(Mission.objects.filter(mission_type='woz').count(), 3)
        self.assertEqual(Mission.objects.filter(mission_year='2016').count(), 8)
        self.assertEqual(Mission.objects.filter(mission_year='2016', mission_type='woz').count(), 2)
        self.assertEqual(Mission.objects.filter(mission_year='2017').count(), 1)
        self.assertEqual(Mission.objects.filter(mission_year='2017', mission_type='bi').count(), 0)

        panos = Panorama.done.all()
        self.assertEqual(panos.count(), 16)

        self.assertIsNotNone(panos[0]._geolocation_2d_rd)
        self.assertAlmostEqual(panos[0]._geolocation_2d_rd, panos[0]._geolocation_2d.transform(28992, clone=True))

        # trajecten = Traject.objects.all()
        # self.assertEqual(trajecten.count(), 16)

        # test old-style attributes
        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].surface_type, 'L')
        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].surface_type, 'W')
        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].surface_type, 'L')

        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].mission_distance, 5)
        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].mission_distance, 10)
        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].mission_distance, 5)

        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].mission_type, 'bi')
        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].mission_type, 'bi')
        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].mission_type, 'woz')

        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].mission_year, 2016)
        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].mission_year, 2016)
        self.assertEqual(Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0].mission_year, 2017)

        # test new-style attributes
        self.assertIn('surface-land', Panorama.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].tags)
        self.assertIn('surface-water', Panorama.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].tags)
        self.assertIn('surface-land', Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].tags)

        self.assertIn('mission-distance-5', Panorama.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].tags)
        self.assertIn('mission-distance-10', Panorama.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].tags)
        self.assertIn('mission-distance-5', Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].tags)

        self.assertIn('mission-bi', Panorama.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].tags)
        self.assertIn('mission-bi', Panorama.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].tags)
        self.assertIn('mission-woz', Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].tags)

        self.assertIn('mission-2016', Panorama.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].tags)
        self.assertIn('mission-2016', Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].tags)
        self.assertIn('mission-2017', Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0].tags)

        recent = RecentPanorama.objects.all()
        self.assertEqual(recent.count(), 14)


    def test_panoramarow_sets_status(self, *args):
        mission = Mission()
        job = ImportPanoramaJob()
        basic_row_fields = {
            'gps_seconds[s]': 2000,
            'longitude[deg]': 50,
            'latitude[deg]': 5,
            'altitude_ellipsoidal[m]': 6.0,
            'roll[deg]': 3.0,
            'pitch[deg]': 7.2,
            'heading[deg]': 320
        }
        row_to_be_rendered = {'panorama_file_name': 'row_to_be_rendered', **basic_row_fields}
        row_rendered = {'panorama_file_name': 'row_rendered', **basic_row_fields}
        row_done = {'panorama_file_name': 'row_done', **basic_row_fields}
        job.files_in_panodir = ['path/row_to_be_rendered.jpg', 'path/row_rendered.jpg', 'path/row_done.jpg']
        job.files_in_renderdir = ['container/path/row_rendered.jpg',
                                  'container/path/row_done.jpg']
        job.files_in_blurdir = ['container/path/row_done/equirectangular/panorama_8000.jpg']

        actual = job.process_panorama_row(row_to_be_rendered, 'container', 'path/', mission)
        self.assertEqual(actual.status, Panorama.STATUS.to_be_rendered)

        actual = job.process_panorama_row(row_rendered, 'container', 'path/', mission)
        self.assertEqual(actual.status, Panorama.STATUS.rendered)

        actual = job.process_panorama_row(row_done, 'container', 'path/', mission)
        self.assertEqual(actual.status, Panorama.STATUS.done)
