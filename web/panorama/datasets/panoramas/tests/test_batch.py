

from django.test import TransactionTestCase

from .. import models, batch


class ImportPanoTest(TransactionTestCase):

    def task(self):
        pass
        # batch.ImportPanoramaJob().process()

    def test_import(self):

        self.task()

        panos = models.Panorama.objects.all()
        self.assertEqual(panos.count(), 14)

        trajecten = models.Traject.objects.all()
        self.assertEqual(trajecten.count(), 14)

