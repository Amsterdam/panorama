from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks','0001_initial')
    ]

    operations = [
        migrations.DeleteModel(
            name='RenderTask',
        ),
    ]
