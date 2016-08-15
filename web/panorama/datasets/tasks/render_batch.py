# Python
import logging
import os.path

# Package
from django.conf import settings

# Project
from datasets.panoramas.models import Panorama


class RenderBatch:
    def clear_rendering(self):
        Panorama.rendering.update(status=Panorama.STATUS.to_be_rendered)

