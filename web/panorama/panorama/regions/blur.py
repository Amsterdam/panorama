import cv2
import numpy as np

from panorama.regions.util import wrap_around


def blur(im, regions):
    """Blur regions in the Image im."""
    im = np.array(im)

    for region in _split_regions(regions):
        (top, left), (bottom, right) = _make_rectangle(region[:-1])
        snippet = im[top:bottom, left:right]
        blur_kernel_size = 2 * int((bottom - top) / 4) + 1
        snippet = cv2.GaussianBlur(
            snippet, (blur_kernel_size, blur_kernel_size), blur_kernel_size,
            dst=snippet,
        )

    return im


def _make_rectangle(points):
    """
    Returns the smallest axis-oriented rectangle that contains all the (x, y) points.
    """
    top = min(p[1] for p in points)
    left = min(p[0] for p in points)
    bottom = max(p[1] for p in points)
    right = max(p[0] for p in points)

    return (top, left), (bottom, right)


def _split_regions(regions):
    """Split regions that wrap around the image border."""
    for region in regions:
        yield from wrap_around(regions)
