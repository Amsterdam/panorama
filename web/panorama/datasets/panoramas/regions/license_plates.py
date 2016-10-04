import io

from numpy import dsplit, squeeze, dstack
from scipy import misc
from scipy.ndimage import map_coordinates
from PIL import Image

from datasets.shared.object_store import ObjectStore
from .cliches import Cliches


class LicensePlateSampler:
    """
    Creates a set of image-samples from a panorama that can be tested for license plates
    """
    object_store = ObjectStore()
    cliches = Cliches()

    def __init__(self, panorama):
        self.panorama = panorama

    def get_image_samples(self):
        samples = []
        panorama_image = misc.fromimage(self._get_raw_image_binary())
        for cliche in self.cliches.all:
            sample = {}
            sample['image'] = self.sample_image(panorama_image, cliche.x, cliche.y)
            sample['original'] = cliche.original
            samples.append(sample)

        return samples

    def sample_image(self, image, x, y):
        # split in 3 channels
        rgb_in = squeeze(dsplit(image, 3))

        # sample_each_channel  //  .T for changing over columns and rows.
        r = map_coordinates(rgb_in[0], [x, y], order=1).T
        g = map_coordinates(rgb_in[1], [x, y], order=1).T
        b = map_coordinates(rgb_in[2], [x, y], order=1).T

        # merge channels
        return dstack((r, g, b))

    def _get_raw_image_binary(self):
        raw_image_location = self.panorama.get_raw_image_objectstore_id()
        raw_image = self.object_store.get_panorama_store_object(raw_image_location)
        return Image.open(io.BytesIO(raw_image))
