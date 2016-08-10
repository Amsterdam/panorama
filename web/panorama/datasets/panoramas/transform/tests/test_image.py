# Python
import datetime
from unittest import TestCase, mock
# Packages
from django.contrib.gis.geos import Point
from django.utils.timezone import utc as UTC_TZ
import factory
import factory.fuzzy
from scipy import misc
# Project
from datasets.panoramas.tests import factories
from datasets.panoramas.transform.transformer import PanoramaTransformer
from datasets.panoramas.models import Panorama

def mock_get_raw_pano(pano):
    path = '/app/panoramas_test/'+pano['container']+'/'+pano['name']
    with open(path, mode='rb') as file:
        return file.read()


class TestTransformImg(TestCase):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas_test folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test datasets.panoramas.transform.tests

    look into the .gitignore-ed directory PROJECT/panoramas_test/output for a visual check on the transformations
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
        factories.PanoramaFactory.create(
            pano_id='TMX7315120208-000067_pano_0011_000463',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename='pano_0011_000463.jpg',
            path='2016/06/06/TMX7315120208-000067/',
            geolocation=Point(4.96113893249052,
                              52.3632599072419,
                              46.0049178628251),
            roll=-7.25543305609142,
            pitch=0.281594736873711,
            heading=295.567147056641,
        )

    @mock.patch('datasets.panoramas.models.Panorama.object_store.get_panorama_store_object',
                side_effect=mock_get_raw_pano)
    def test_transform_runs_without_errors(self, mock_1):

        images = [
            Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0],
            Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0],
        ]

        for img in images:
            image_tranformer = PanoramaTransformer(img)
            output_path = "/app/panoramas_test/2016/output/"+img.filename[:-4]
            for direction in [0, 90, 180, 270]:
                img1 = image_tranformer.get_translated_image(target_width=900,
                                                             target_fov=80,
                                                             target_horizon=0.3,
                                                             target_heading=direction,
                                                             target_aspect=4/3)
                misc.imsave(output_path+"_{}.jpg".format(direction), img1)
                img1 = image_tranformer.get_translated_image(target_width=450,
                                                             target_fov=80,
                                                             target_horizon=0.3,
                                                             target_heading=direction,
                                                             target_aspect=4/3)
                misc.imsave(output_path+"_small_{}.jpg".format(direction), img1)

            img1 = image_tranformer.get_translated_image()
            misc.imsave(output_path+"_trans.jpg", img1)


