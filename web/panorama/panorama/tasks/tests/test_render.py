import datetime
import logging
import os
from unittest import TestCase, mock, skipIf

import factory
import factory.fuzzy
from django.contrib.gis.geos import Point
from django.utils.timezone import utc as UTC_TZ

from datasets.panoramas.models import Panoramas
from datasets.panoramas.tests import factories
from panorama.transform.tests.test_img_file import mock_get_raw_pano
from ..worker import PanoRenderer

log = logging.getLogger(__name__)


@skipIf(not os.path.exists('/app/panoramas_test'),
        'Render test skipped: no mounted directory found, run in docker container')
class TestRender(TestCase):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test panorama.tasks.tests

    look into the .gitignore-ed directory PROJECT/panoramas_test/output for a visual check on the transformations
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        for pano in Panoramas.objects.all():
            pano.status = Panoramas.STATUS.rendered
            pano.save()

        try:
            pano = Panoramas.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0]
            pano.status = Panoramas.STATUS.to_be_rendered
            pano.save()
        except IndexError:
            factories.PanoramaFactory.create(
                pano_id='TMX7315120208-000073_pano_0004_000087',
                timestamp=factory.fuzzy.FuzzyDateTime(
                    datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ),
                    force_year=2014),
                filename='pano_0004_000087.jpg',
                path='2016/06/09/TMX7315120208-000073/',
                geolocation=Point(4.89593266865189,
                                  52.3717022854865,
                                  47.3290048856288),
                roll=-5.48553832377717,
                pitch=-6.76660799409535,
                heading=219.760795827427,
                mission_distance=5.0,
                mission_year="2016",
                tags=[]
            )

    @mock.patch('panorama.transform.utils_img_file.object_store.put_into_panorama_store')
    @mock.patch('panorama.transform.utils_img_file.get_raw_panorama_as_rgb_array',
                side_effect=mock_get_raw_pano)
    def test_create_and_render_batch(self, mock_read_raw, mock_write_transformed):
        to_render = Panoramas.to_be_rendered.all()[0]
        self.assertEquals('TMX7315120208-000073_pano_0004_000087', to_render.pano_id)

        PanoRenderer().process()
        self.assertEquals(0, len(Panoramas.to_be_rendered.all()))
        self.assertTrue(mock_read_raw.called, msg='Read Raw was not called')
        self.assertTrue(mock_write_transformed.called, msg='Write transformed was not called')
