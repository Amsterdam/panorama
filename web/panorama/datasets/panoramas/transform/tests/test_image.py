# Python
import datetime, os, logging
from unittest import TestCase, mock, skipIf
from math import log as logarithm
# Packages
from django.contrib.gis.geos import Point
from django.utils.timezone import utc as UTC_TZ
import factory
import factory.fuzzy
from scipy import misc
from PIL import Image
# Project
from datasets.panoramas.tests import factories
from datasets.panoramas.transform.transformer import PanoramaTransformer
from datasets.panoramas.models import Panorama

log = logging.getLogger(__name__)

MAX_WIDTH=2048
TILE_SIZE=512
PREVIEW_WIDTH=256


def set_pano(pano):
    global panorama
    panorama = pano


def mock_get_raw_pano(pano):
    path = '/app/panoramas_test/'+pano['container']+'/'+pano['name']
    return Image.open(path)


@skipIf(not os.path.exists('/app/panoramas_test'),
        'Render test skipped: no mounted directory found, run in docker container')
class TestTransformImg(TestCase):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas_test folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test datasets.panoramas.transform.tests.test_image

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

    @mock.patch('datasets.panoramas.transform.transformer.PanoramaTransformer._get_raw_image_binary',
                side_effect=mock_get_raw_pano)
    def test_transform_runs_without_errors(self, mock_1):

        images = [
            Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0],
            Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0],
        ]

        for img in images:
            set_pano(img)
            image_tranformer = PanoramaTransformer(img.get_raw_image_objectstore_id(), img.heading, img.pitch, img.roll)
            output_path = "/app/test_output/"+img.filename[:-4]
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

            img1 = image_tranformer.get_translated_image(target_width=8000)
            transformed = Image.fromarray(img1)
            transformed.save(output_path+"_8000.jpg", optimize=True, progressive=True)
            half_size = transformed.resize((4000, 2000), Image.ANTIALIAS)
            half_size.save(output_path+"_4000.jpg", optimize=True, progressive=True)
            smallest = transformed.resize((2000, 1000), Image.ANTIALIAS)
            smallest.save(output_path+"_2000.jpg", optimize=True, progressive=True)

    @mock.patch('datasets.panoramas.transform.transformer.PanoramaTransformer._get_raw_image_binary',
                side_effect=mock_get_raw_pano)
    def test_transform_cubic_runs_without_errors(self, mock_1):

        images = [
            Panorama.objects.filter(pano_id='TMX7315120208-000073_pano_0004_000087')[0],
            Panorama.objects.filter(pano_id='TMX7315120208-000067_pano_0011_000463')[0],
        ]

        for img in images:
            set_pano(img)
            image_tranformer = PanoramaTransformer(img.get_raw_image_objectstore_id(), img.heading, img.pitch, img.roll)
            output_path = "/app/test_output/"+img.filename[:-4]
            img_set = image_tranformer.get_cubic_projections(target_width=MAX_WIDTH)
            previews = {}
            for side, img in img_set.items():
                cube_face = Image.fromarray(img)
                preview = cube_face.resize((PREVIEW_WIDTH, PREVIEW_WIDTH), Image.ANTIALIAS)
                previews[side] = preview
                for zoomlevel in range(0, 1+int(logarithm(MAX_WIDTH/TILE_SIZE, 2))):
                    zoom_size = 2 ** zoomlevel * TILE_SIZE
                    zoomed_img = cube_face.resize((zoom_size, zoom_size), Image.ANTIALIAS)
                    for h_idx, h_start in enumerate(range(0, zoom_size, TILE_SIZE)):
                        for v_idx, v_start in enumerate(range(0, zoom_size, TILE_SIZE)):
                            tile = zoomed_img.crop((h_start, v_start, h_start+TILE_SIZE, v_start+TILE_SIZE))
                            tile_path = "/{}/{}/{}".format(zoomlevel+1, side, v_idx)
                            os.makedirs(output_path+tile_path, exist_ok=True)
                            tile.save("{}{}/{}.jpg".format(output_path, tile_path, h_idx),  optimize=True, progressive=True)

            preview_image = Image.new('RGB', (PREVIEW_WIDTH, 6 * PREVIEW_WIDTH))
            for idx, side in enumerate(['b', 'd', 'f', 'l', 'r', 'u']):
                preview_image.paste(previews[side], (0,PREVIEW_WIDTH*idx))
            preview_image.save(output_path+"/preview.jpg", "JPEG", optimize=True, progressive=True)


