# Python
import logging
import os.path

# Package
from django.conf import settings

# Project
from datasets.panoramas.models import Panorama
from datasets.tasks.models import RenderTask

log = logging.getLogger(__name__)


class CreateRenderBatch:

    def process(self):
        for pano in Panorama.objects.all():

            if os.path.isfile(pano.get_full_raw_path()) \
                    and not os.path.isfile(pano.get_full_rendered_path()):
                task = RenderTask(pano_id=pano.pano_id)
                task.save()
