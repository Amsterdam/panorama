from PIL import Image
from numpy import asarray, dsplit, squeeze


def mock_get_raw_pano(pano_url):
    path = '/app/panoramas_test/' + pano_url
    panorama_image = asarray(Image.open(path))
    return squeeze(dsplit(panorama_image, 3))

