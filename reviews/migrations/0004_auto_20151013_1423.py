# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_review_stage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='date_end',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='decision',
            unique_together=set([('review', 'reviewer')]),
        ),
    ]
