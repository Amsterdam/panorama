# Python
import logging
import os.path

# Package
from django.conf import settings

# Project
from datasets.panoramas.models import Panorama


class RenderBatch:
    def clear_rendering(self):
        for pano_rendering in Panorama.rendering.all():
            pano_rendering.status = Panorama.STATUS.to_be_rendered
            pano_rendering.save()

