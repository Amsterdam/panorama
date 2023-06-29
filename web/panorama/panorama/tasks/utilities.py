from django.db import transaction
from datasets.panoramas.models import Panorama


def reset_abandoned_work():
    with transaction.atomic():
        Panorama.blurring.all().update(status=Panorama.STATUS.detected)
        Panorama.detecting_regions.all().update(status=Panorama.STATUS.rendered)
        Panorama.rendering.all().update(status=Panorama.STATUS.to_be_rendered)


def call_for_close():
    # here the Jenkins job for closing the swarm down should be called
    pass
