# Python
import datetime
from unittest import TestCase
# Packages
from django.contrib.gis.geos import Point
from django.utils.timezone import utc as UTC_TZ
import factory
import factory.fuzzy
# Project
from datasets.panoramas.tests import factories
from datasets.panoramas.models import Panorama


class TestTransformer(TestCase):

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

        try:
            Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0]
        except IndexError:
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
                mission_distance=5.0,
                mission_year="2016",
                tags=[]
            )

        cls.images = [
            Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0],
            Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0],
        ]

