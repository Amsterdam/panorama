from django.db import transaction
from datasets.panoramas.models import Panoramas


def reset_abandoned_work():
    with transaction.atomic():
        Panoramas.blurring.all().update(status=Panoramas.STATUS.detected)
        Panoramas.detecting_regions.all().update(status=Panoramas.STATUS.rendered)
        Panoramas.rendering.all().update(status=Panoramas.STATUS.to_be_rendered)


def call_for_close():
    # here the Jenkins job for closing the swarm down should be called
    pass
