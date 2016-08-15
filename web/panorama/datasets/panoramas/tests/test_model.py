from unittest import TestCase, mock
import random, string

from django.contrib.gis.geos import Point

from .. import models


def randomword(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

fake_object = randomword(24)
fake_io = randomword(24)
fake_img = randomword(24)


def get_object(_):
    return fake_object


def get_io(_):
    return fake_io


def get_img(_):
    return fake_img


class TestModel(TestCase):
    fcontainer = randomword(length=10)
    fpath = randomword(length=12)
    fname = randomword(length=24)
    p = models.Panorama(path=fcontainer+'/'+fpath, filename=fname+'.jpg', geolocation=Point(1,1,1))

    def test_img_url(self):
        self.assertTrue('/'+self.fpath+'/'+self.fname+'_normalized.jpg', self.p.img_url)


    @mock.patch('PIL.Image.open', side_effect=get_img)
    @mock.patch('io.BytesIO', side_effect=get_io)
    @mock.patch('datasets.shared.object_store.ObjectStore.get_panorama_store_object', side_effect=get_object)
    def test_get_raw_binary(self, mock_object_store, mock_io, mock_img):
        actual = self.p.get_raw_image_binary()
        mock_object_store.assert_called_with({'container':self.fcontainer, 'name':self.fpath+self.fname+'.jpg'})
        mock_io.assert_called_with(fake_object)
        mock_img.assert_called_with(fake_io)
        self.assertEqual(actual, fake_img)
