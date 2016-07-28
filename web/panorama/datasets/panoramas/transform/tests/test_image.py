# Python
import datetime
import unittest
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


class TestTransformImg(unittest.TestCase):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test

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
            path='/2016/06/09/TMX7315120208-000073',
            geolocation=Point(4.89593266865189,
                              52.3717022854865,
                              47.3290048856288),
            roll=-5.48553832377717,
            pitch=-6.76660799409535,
            heading=219.760795827427,
        )
        factories.PanoramaFactory.create(
            pano_id='TMX7315120208-000073_pano_0004_000183',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename='pano_0004_000183.jpg',
            path='/2016/06/09/TMX7315120208-000073',
            geolocation=Point(4.90015282534372,
                              52.3752177982126,
                              45.951653891243),
            roll=-9.21269897979498,
            pitch=-3.30786024502109,
            heading=212.257469600853,
        )
        factories.PanoramaFactory.create(
            pano_id='TMX7315120208-000073_pano_0005_001111',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename='pano_0005_001111.jpg',
            path='/2016/06/09/TMX7315120208-000073',
            geolocation=Point(4.88584822835825,
                              52.3856824065041,
                              47.984863370657),
            roll=0.345581504432213,
            pitch=-7.13402615732958,
            heading=274.852145585679,
        )
        factories.PanoramaFactory.create(
            pano_id='TMX7315120208-000072_pano_0007_000072',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename='pano_0007_000072.jpg',
            path='/2016/06/08/TMX7315120208-000072',
            geolocation=Point(4.91250404103872,
                              52.3745885115937,
                              46.1886808034033),
            roll=-0.278491861965009,
            pitch=-11.7292454216082,
            heading=174.587862640275,
        )
        factories.PanoramaFactory.create(
            pano_id='TMX7315120208-000030_pano_0000_000853',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename='pano_0000_000853.jpg',
            path='/2016/04/18/TMX7315120208-000030',
            geolocation=Point(4.93665401561895,
                              52.3551484757251,
                              37.6860034232959),
            roll=0.00250335697206269,
            pitch=0.00307567328046648,
            heading=317.099215937017,
        )
        factories.PanoramaFactory.create(
            pano_id='TMX7315120208-000038_pano_0002_000466',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename='pano_0002_000466.jpg',
            path='/2016/05/09/TMX7315120208-000038',
            geolocation=Point(5.02513104599607,
                              52.4096209630701,
                              43.5107887201011),
            roll=-7.52986233794669,
            pitch=0.0836336272319252,
            heading=187.367676600977,
        )
        factories.PanoramaFactory.create(
            pano_id='TMX7315120208-000067_pano_0011_000463',
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename='pano_0011_000463.jpg',
            path='/2016/06/06/TMX7315120208-000067',
            geolocation=Point(4.96113893249052,
                              52.3632599072419,
                              46.0049178628251),
            roll=-7.25543305609142,
            pitch=0.281594736873711,
            heading=295.567147056641,
        )

    def test_transform_runs_without_errors(self):

        images = [
            Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0],
            Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000183')[0],
            Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0005_001111')[0],
            Panorama.objects.filter(pano_id='TMX7315120208-000072_pano_0007_000072')[0],
            Panorama.objects.filter(pano_id='TMX7315120208-000030_pano_0000_000853')[0],
            Panorama.objects.filter(pano_id='TMX7315120208-000038_pano_0002_000466')[0],
            Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0],
        ]

        for img in images:
            it = PanoramaTransformer(img)
            output_path = "/app/panoramas_test/2016/output/"+img.filename[:-4]
            for direction in [0, 90, 180, 270]:
                img1 = it.get_translated_image(target_width=900,
                                               target_fov=80,
                                               target_horizon=0.3,
                                               target_heading=direction,
                                               target_aspect=4/3)
                misc.imsave(output_path+"_{}.jpg".format(direction), img1)
                img1 = it.get_translated_image(target_width=450,
                                               target_fov=80,
                                               target_horizon=0.3,
                                               target_heading=direction,
                                               target_aspect=4/3)
                misc.imsave(output_path+"_small_{}.jpg".format(direction), img1)

            img1 = it.get_translated_image()
            misc.imsave(output_path+"_trans.jpg", img1)


