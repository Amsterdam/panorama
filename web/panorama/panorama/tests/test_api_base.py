# Python
import datetime, time
# Packages
from django.contrib.gis.geos import Point
from django.utils.timezone import utc as UTC_TZ
import factory
import factory.fuzzy
from rest_framework.test import APITestCase
# Project
from datasets.panoramas.models import Panorama
from datasets.panoramas.tests import factories
from panorama.management.commands.refresh_views import Command as RefreshViews


class PanoramaApiTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Adding locations
        factories.PanoramaFactory.create(
            pano_id='PANO_1_2014',
            status=Panorama.STATUS.done,
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.94433, 52.35101, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
            mission_distance=5.0,
            mission_year=2014
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_2_2014_CLOSE',
            status=Panorama.STATUS.done,
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.94432, 52.35102, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
            mission_distance=5.0,
            mission_year=2014
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_3_2015_CLOSE',
            status=Panorama.STATUS.done,
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2015, 1, 1, tzinfo=UTC_TZ), force_year=2015),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.94431, 52.35103, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
            mission_distance=5.0,
            mission_year=2015
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_5_2014_CLOSE_BUT_NO_CIGAR',
            status=Panorama.STATUS.detected,
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2014, 1, 1, tzinfo=UTC_TZ), force_year=2014),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.94439711277457, 52.3510810574283, 12),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
            mission_distance=5.0,
            mission_year=2014
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_5_2015_CLOSE_BUT_NO_CIGAR',
            status=Panorama.STATUS.to_be_rendered,
            timestamp=factory.fuzzy.FuzzyDateTime(
                datetime.datetime(2015, 1, 1, tzinfo=UTC_TZ), force_year=2015),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.897, 52.377, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
            mission_distance=5.0,
            mission_year=2015
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_6_2016_CLOSE',
            status=Panorama.STATUS.done,
            timestamp=datetime.datetime(2016, 5, 5, tzinfo=UTC_TZ),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.89707, 52.37795, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
            mission_distance=5.0,
            mission_year=2016
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_7_2016_CLOSE_BUT_NO_CIGAR',
            status=Panorama.STATUS.done,
            timestamp=datetime.datetime(2016, 5, 5, tzinfo=UTC_TZ),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.8970, 52.377956, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
            mission_distance=5.0,
            mission_year=2016
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_8_2017_CLOSE',
            status=Panorama.STATUS.done,
            timestamp=datetime.datetime(2017, 5, 5, tzinfo=UTC_TZ),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.89708, 52.37794, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
            mission_distance=5.0,
            mission_year=2017
        )
        factories.PanoramaFactory.create(
            pano_id='PANO_9_2017_CLOSE_BUT_NO_CIGAR',
            status=Panorama.STATUS.done,
            timestamp=datetime.datetime(2017, 5, 5, tzinfo=UTC_TZ),
            filename=factory.fuzzy.FuzzyText(length=30),
            path=factory.fuzzy.FuzzyText(length=30),
            geolocation=Point(4.897071, 52.377956, 10),
            roll=factory.fuzzy.FuzzyFloat(-10, 10),
            pitch=factory.fuzzy.FuzzyFloat(-10, 10),
            heading=factory.fuzzy.FuzzyFloat(-10, 10),
            mission_distance=5.0,
            mission_year=2017
        )

        RefreshViews().refresh_views()
        time.sleep(2)
