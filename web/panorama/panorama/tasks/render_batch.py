# Project
from datasets.panoramas.models import Panorama


class RenderBatch:
    def clear_rendering(self):
        Panorama.rendering.update(status=Panorama.STATUS.to_be_rendered)

