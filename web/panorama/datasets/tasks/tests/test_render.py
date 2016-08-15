# Python
import datetime, os
from unittest import TestCase, mock, skipIf
# Packages
import factory
import factory.fuzzy
from django.contrib.gis.geos import Point
from django.utils.timezone import utc as UTC_TZ
# Project
from datasets.panoramas.tests import factories
from datasets.panoramas.models import Panorama
from .. import render_task


def mock_get_raw_pano(pano):
    path = '/app/panoramas_test/'+pano['container']+'/'+pano['name']
    with open(path, mode='rb') as file:
        return file.read()


@skipIf(not os.path.exists('/app/panoramas_test'),
        'Render test skipped: no mounted directory found, run in docker container')
class TestRender(TestCase):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test datasets.tasks.tests

    look into the .gitignore-ed directory PROJECT/panoramas_test/output for a visual check on the transformations
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        for pano in Panorama.objects.all():
            pano.status = Panorama.STATUS.rendered
            pano.save()

        try:
            pano = Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0]
            pano.status = Panorama.STATUS.to_be_rendered
            pano.save()
        except IndexError:
            factories.PanoramaFactory.create(
                pano_id='TMX7315120208-000073_pano_0004_000087',
                timestamp=factory.fuzzy.FuzzyDateTime(
                    datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
                filename='pano_0004_000087.jpg',
                path='2016/06/09/TMX7315120208-000073/',
                geolocation=Point(4.89593266865189,
                                  52.3717022854865,
                                  47.3290048856288),
                roll=-5.48553832377717,
                pitch=-6.76660799409535,
                heading=219.760795827427,
            )


    @mock.patch('datasets.tasks.render_task.RenderPanorama.object_store.put_into_datapunt_store')
    @mock.patch('datasets.panoramas.models.Panorama.object_store.get_panorama_store_object',
                side_effect=mock_get_raw_pano)
    def test_create_and_render_batch(self, mock_read_raw, mock_write_transformed):
        to_render = Panorama.to_be_rendered.all()[0]
        self.assertEquals('TMX7315120208-000073_pano_0004_000087', to_render.pano_id)

        render_task.RenderPanorama().process()
        self.assertEquals(0, len(Panorama.to_be_rendered.all()))
        self.assertTrue(mock_read_raw.called)
        self.assertTrue(mock_write_transformed.called)
