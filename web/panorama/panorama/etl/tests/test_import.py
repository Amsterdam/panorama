import glob
import logging
import os
from pathlib import Path

from django.test import TransactionTestCase
from unittest import mock, skipIf

from datasets.panoramas.models import Panoramas, Traject, Mission
from panorama.etl.batch_import import import_mission_metadata, rebuild_mission
from panorama.etl.data_to_model import process_panorama_row

log = logging.getLogger(__name__)


def mock_get_csvs(csv_type):
    files = []
    if csv_type == 'panorama':
        files = glob.glob('/app/panoramas_test/**/panorama*.csv', recursive=True)
    if csv_type == 'trajectory':
        files = glob.glob('/app/panoramas_test/**/trajectory.csv', recursive=True)
    return [{'container': '1', 'name': f} for f in files]


def mock_get_csv_type(container, mission_path, csv_type):
    files = []
    if csv_type == 'panorama':
        files = glob.glob(f'/app/panoramas_test/{container}/{mission_path}panorama*.csv',
                          recursive=True)
    return [{'container': '1', 'name': f} for f in files]


def mock_get_root_csvs(csv_type):
    files = []
    if csv_type == 'missiegegevens':
        files = glob.glob('/app/panoramas_test/**/missiegegevens.csv', recursive=True)
    return [{'container': '1', 'name': f} for f in files]


def mock_get_csv(csv):
    with open(csv['name'], mode='rb') as file:
        return file.read()


def mock_file_exists(_, path, filename):
    file = f'{path}/{filename}'
    return Path(file).is_file()


mock_objectstore = 'panorama.etl.batch_import.objectstore.%s'
file_exists = True
blurred_file_exists = False
rendered_file_exists = False


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
    @mock.patch(mock_objectstore % 'get_csv_type', side_effect=mock_get_csv_type)
    @mock.patch(mock_objectstore % 'get_containerroot_csvs', side_effect=mock_get_root_csvs)
    @mock.patch(mock_objectstore % 'get_panorama_store_object', side_effect=mock_get_csv)
    @mock.patch("panorama.etl.data_to_model.panorama_image_file_exists", side_effect=mock_file_exists)
    @mock.patch("panorama.etl.data_to_model.panorama_blurred_file_exists",
                side_effect=lambda a, b, c: blurred_file_exists)
    @mock.patch("panorama.etl.data_to_model.panorama_rendered_file_exists",
                side_effect=lambda a, b, c: rendered_file_exists)
    def test_import(self, *args):
        import_mission_metadata()
        for (container, mission_path) in [('2016', '03/21/TMX7315120208-000021/'),
                                          ('2016', '03/24/TMX7315120208-000022/'),
                                          ('2016', '04/18/TMX7315120208-000029/'),
                                          ('2016', '04/18/TMX7315120208-000030/'),
                                          ('2016', '04/19/TMX7315120208-000032/'),
                                          ('2016', '04/19/TMX7315120208-000033/'),
                                          ('2016', '05/09/TMX7315120208-000038/'),
                                          ('2016', '06/06/TMX7315120208-000067/'),
                                          ('2016', '06/08/TMX7315120208-000072/'),
                                          ('2016', '06/09/TMX7315120208-000073/'),
                                          ('2017', '03/21/TMX7315120208-100021/')]:
            rebuild_mission(container, mission_path)

        for pano in Panoramas.objects.all():
            pano.status = Panoramas.STATUS.done
            pano.save()

        missies = Mission.objects.all()
        self.assertEqual(missies.count(), 9)

        self.assertEqual(Mission.objects.filter(surface_type='L').count(), 5)
        self.assertEqual(Mission.objects.filter(surface_type='W').count(), 4)
        self.assertEqual(Mission.objects.filter(mission_distance=5).count(), 5)
        self.assertEqual(Mission.objects.filter(mission_distance=10).count(), 4)
        self.assertEqual(Mission.objects.filter(mission_type='bi').count(), 6)
        self.assertEqual(Mission.objects.filter(mission_type='woz').count(), 3)
        self.assertEqual(Mission.objects.filter(mission_year='2016').count(), 8)
        self.assertEqual(Mission.objects.filter(mission_year='2016', mission_type='woz').count(), 2)
        self.assertEqual(Mission.objects.filter(mission_year='2017').count(), 1)
        self.assertEqual(Mission.objects.filter(mission_year='2017', mission_type='bi').count(), 0)

        panos = Panoramas.done.all()
        self.assertEqual(panos.count(), 16)

        self.assertIsNotNone(panos[0]._geolocation_2d_rd)
        self.assertAlmostEqual(panos[0]._geolocation_2d_rd, panos[0]._geolocation_2d.transform(28992, clone=True))

        # trajecten = Traject.objects.all()
        # self.assertEqual(trajecten.count(), 16)

        # test old-style attributes
        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].surface_type, 'L')
        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].surface_type, 'W')
        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].surface_type, 'L')

        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].mission_distance, 5)
        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].mission_distance, 10)
        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].mission_distance, 5)

        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].mission_type, 'bi')
        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].mission_type, 'bi')
        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].mission_type, 'woz')

        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].mission_year, 2016)
        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].mission_year, 2016)
        self.assertEqual(Panoramas.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0].mission_year, 2017)

        # test new-style attributes
        self.assertIn('surface-land', Panoramas.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].tags)
        self.assertIn('surface-water', Panoramas.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].tags)
        self.assertIn('surface-land', Panoramas.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].tags)

        self.assertIn('mission-distance-5', Panoramas.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].tags)
        self.assertIn('mission-distance-10', Panoramas.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].tags)
        self.assertIn('mission-distance-5', Panoramas.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].tags)

        self.assertIn('mission-bi', Panoramas.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].tags)
        self.assertIn('mission-bi', Panoramas.objects.filter(pano_id='TMX7315120208-000033_pano_0000_006658')[0].tags)
        self.assertIn('mission-woz', Panoramas.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].tags)

        self.assertIn('mission-2016', Panoramas.objects.filter(pano_id='TMX7315120208-000032_pano_0000_007572')[0].tags)
        self.assertIn('mission-2016', Panoramas.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0].tags)
        self.assertIn('mission-2017', Panoramas.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0].tags)

    @mock.patch("panorama.etl.data_to_model.panorama_image_file_exists",
                side_effect=lambda a, b, c: file_exists)
    @mock.patch("panorama.etl.data_to_model.panorama_blurred_file_exists",
                side_effect=lambda a, b, c: blurred_file_exists)
    @mock.patch("panorama.etl.data_to_model.panorama_rendered_file_exists",
                side_effect=lambda a, b, c: rendered_file_exists)
    def test_panoramarow_sets_status(self, *args):
        global file_exists, blurred_file_exists, rendered_file_exists

        basic_row_fields = {
            'gps_seconds[s]': 2000,
            'longitude[deg]': 50,
            'latitude[deg]': 5,
            'altitude_ellipsoidal[m]': 6.0,
            'roll[deg]': 3.0,
            'pitch[deg]': 7.2,
            'heading[deg]': 320
        }

        file_exists, blurred_file_exists, rendered_file_exists = True, False, False
        row_to_be_rendered = {'panorama_file_name': 'row_to_be_rendered', **basic_row_fields}
        actual = process_panorama_row(row_to_be_rendered.keys(),
                                      row_to_be_rendered.values(),
                                      {'container': 'container', 'name': 'path/mission'})
        self.assertEqual(actual.status, Panoramas.STATUS.to_be_rendered)

        file_exists, blurred_file_exists, rendered_file_exists = True, False, True
        row_rendered = {'panorama_file_name': 'row_rendered', **basic_row_fields}
        actual = process_panorama_row(row_rendered.keys(),
                                      row_rendered.values(),
                                      {'container': 'container', 'name': 'path/mission'})
        self.assertEqual(actual.status, Panoramas.STATUS.rendered)

        file_exists, blurred_file_exists, rendered_file_exists = True, True, True
        row_done = {'panorama_file_name': 'row_done', **basic_row_fields}
        actual = process_panorama_row(row_done.keys(),
                                      row_done.values(),
                                      {'container': 'container', 'name': 'path/mission'})
        self.assertEqual(actual.status, Panoramas.STATUS.done)
