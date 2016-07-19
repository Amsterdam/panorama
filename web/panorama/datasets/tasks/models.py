from django.db import models


class RenderTask(models.Model):
    pano_id = models.CharField(max_length=37, primary_key=True)

    def __str__(self):
        return '<RenderTask %d>' % self.pano_id