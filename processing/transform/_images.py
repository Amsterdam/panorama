import io
import warnings

import kornia
import numpy as np
from PIL import Image
import torch


def _image_from_tensor(im: torch.Tensor) -> Image.Image:
    im = im.to(device="cpu", dtype=torch.uint8).numpy()
    return Image.fromarray(im.transpose(1, 2, 0), "RGB")


def jpeg_from_tensor(im: torch.Tensor, quality=80) -> bytes:
    """Save a tensor as a JPEG, in-memory.

    The tensor im should have shape 3×H×W.
    """
    im = _image_from_tensor(im)
    out = io.BytesIO()
    im.save(out, format="JPEG", optimize=True, quality=quality)
    return out.getvalue()


def resize(im: torch.Tensor, width: int) -> torch.Tensor:
    # Kornia's resize w/ antialias produces results similar to PIL.
    if not im.dtype.is_floating_point:
        im = im.to(dtype=torch.float32)
    return kornia.geometry.transform.resize(im, size=width, side="long", antialias=True)


def tensor_from_jpeg(b: bytearray | bytes, device="cpu") -> torch.Tensor:
    """Load a tensor from a JPEG image in memory.

    The returned tensor will have dtype=torch.uint8 and shape 3×H×W.
    """
    im = Image.open(io.BytesIO(b))
    im = np.asarray(im).transpose(2, 0, 1)
    with warnings.catch_warnings():
        # On device="cpu", we don't want to copy the array.
        # We'll be careful to treat it as read-only.
        warnings.filterwarnings("ignore", "non-writable tensors")
        return torch.as_tensor(im, device=device)
