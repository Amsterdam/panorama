# Python
import datetime
import unittest
import os.path
# Packages
from django.contrib.gis.geos import Point
from django.utils.timezone import utc as UTC_TZ
import factory
import factory.fuzzy
# Project
from datasets.panoramas.tests import factories
from datasets.tasks.models import RenderTask
from datasets.panoramas.models import Panorama
from .. import render_batch, render_task

class TestRender(unittest.TestCase):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test datasets.tasks.tests

    look into the .gitignore-ed directory PROJECT/panoramas_test/output for a visual check on the transformations
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0]
        except IndexError:
            factories.PanoramaFactory.create(
                pano_id='TMX7315120208-000073_pano_0004_000087',
                timestamp=factory.fuzzy.FuzzyDateTime(
                    datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
                filename='pano_0004_000087.jpg',
                path='/2016/06/09/TMX7315120208-000073',
                geolocation=Point(4.89593266865189,
                                  52.3717022854865,
                                  47.3290048856288),
                roll=-5.48553832377717,
                pitch=-6.76660799409535,
                heading=219.760795827427,
            )

    def setUp(self):
        self.created_pano = Panorama.objects.filter(
            pano_id='TMX7315120208-000073_pano_0004_000087')[0]
        try:
            os.rename(self.created_pano.get_full_rendered_path(),
                      self.created_pano.get_full_rendered_path()+'_hidden')
        except OSError:
            pass

    def tearDown(self):
        try:
            os.remove(self.created_pano.get_full_rendered_path())
        except OSError:
            pass
        try:
            os.rename(self.created_pano.get_full_rendered_path()+'_hidden',
                      self.created_pano.get_full_rendered_path())
        except OSError:
            pass

    def test_create_and_render_batch(self):
        render_batch.CreateRenderBatch().process()
        task = RenderTask.objects.all()[0]
        self.assertEquals('TMX7315120208-000073_pano_0004_000087', task.pano_id)

        pano = Panorama.objects.filter(pano_id=task.pano_id)[0]
        self.assertFalse(os.path.isfile(pano.get_full_rendered_path()))

        render_task.RenderPanorama().process()
        self.assertEquals(0, len(RenderTask.objects.all()))
        self.assertTrue(os.path.isfile(pano.get_full_rendered_path()))
