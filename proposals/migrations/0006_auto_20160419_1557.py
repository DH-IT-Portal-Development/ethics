# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0005_remove_proposal_has_multiple_groups'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proposal',
            old_name='has_multiple_trajectories',
            new_name='studies_similar',
        ),
    ]
