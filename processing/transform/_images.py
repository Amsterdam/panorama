import io

import numpy as np
from PIL import Image
import torch


def jpeg_from_tensor(im: torch.Tensor, quality=80) -> bytes:
    """Save a tensor as a JPEG, in-memory.

    The tensor im should have shape 3×H×W.
    """
    im = im.to(device="cpu", dtype=torch.uint8).numpy()
    im = Image.fromarray(im.transpose(1, 2, 0), "RGB")
    out = io.BytesIO()
    im.save(out, format="JPEG", optimize=True, quality=quality)
    return out.getvalue()


def tensor_from_jpeg(b: bytearray | bytes, device="cpu") -> torch.Tensor:
    """Load a tensor from a JPEG image in memory.

    The returned tensor will have dtype=torch.uint8 and shape 3×H×W.
    """
    im = Image.open(io.BytesIO(b))
    im = np.asarray(im).transpose(2, 0, 1)
    return torch.as_tensor(im, device=device)
