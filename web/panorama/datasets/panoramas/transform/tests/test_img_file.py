from PIL import Image
from numpy import squeeze, dsplit
from scipy import misc


def mock_get_raw_pano(pano_url):
    path = '/app/panoramas_test/' + pano_url
    panorama_image = misc.fromimage(Image.open(path))
    return squeeze(dsplit(panorama_image, 3))

