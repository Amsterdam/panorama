import io

from numpy import squeeze, dsplit, dstack
from scipy import misc
from scipy.ndimage import map_coordinates
from PIL import Image

from datasets.shared.object_store import ObjectStore

object_store = ObjectStore()


def get_panorama_rgb_array(objectstore_id):
    # read image as numpy array
    raw_image = object_store.get_panorama_store_object(objectstore_id)
    panorama_image = misc.fromimage(Image.open(io.BytesIO(raw_image)))

    # split image in the 3 RGB channels
    return squeeze(dsplit(panorama_image, 3))


def sample_image(coordinates, rgb_array):
    x = coordinates[0]
    y = coordinates[1]

    # resample each channel of the source image
    r = map_coordinates(rgb_array[0], [y, x], order=1)
    g = map_coordinates(rgb_array[1], [y, x], order=1)
    b = map_coordinates(rgb_array[2], [y, x], order=1)

    # merge channels
    return dstack((r, g, b))
