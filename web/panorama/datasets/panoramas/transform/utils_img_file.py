import io

from numpy import squeeze, dsplit, dstack
from scipy import misc
from scipy.ndimage import map_coordinates
from PIL import Image

from datasets.shared.object_store import ObjectStore

object_store = ObjectStore()


def get_panorama_rgb_array(panorama_url):
    # construct objectstore_id
    container = panorama_url.split('/')[0]
    name = panorama_url.replace(container+'/', '')
    objectstore_id = {'container':container, 'name':name}

    # read image as numpy array
    raw_image = object_store.get_panorama_store_object(objectstore_id)
    panorama_image = misc.fromimage(Image.open(io.BytesIO(raw_image)))

    return get_rgb_channels(panorama_image)


def get_rgb_channels(image):
    # split image in the 3 RGB channels
    return squeeze(dsplit(image, 3))


def sample_image(coordinates, rgb_array):
    x = coordinates[0]
    y = coordinates[1]

    # resample each channel of the source image
    r = map_coordinates(rgb_array[0], [y, x], order=1)
    g = map_coordinates(rgb_array[1], [y, x], order=1)
    b = map_coordinates(rgb_array[2], [y, x], order=1)

    # merge channels
    return dstack((r, g, b))


def save_image(image, name):
    byte_array = io.BytesIO()
    image.save(byte_array, format='JPEG', optimize=True, progressive=True)
    object_store.put_into_datapunt_store(name, byte_array.getvalue(), 'image/jpeg')


def roll_left(image, shift, width, height):
    part1 = image.crop((0, 0, shift, height))
    part2 = image.crop((shift, 0, width, height))
    part1.load()
    part2.load()
    output = Image.new('RGB', (width, height))
    output.paste(part2, (0, 0, width-shift, height))
    output.paste(part1, (width-shift, 0, width, height))

    return output


def image2byte_array(image: Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='JPEG')
    return imgByteArr.getvalue()


