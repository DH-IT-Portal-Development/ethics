# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0020_auto_20160318_2108'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intervention',
            name='study',
        ),
        migrations.AlterField(
            model_name='proposal',
            name='applicants',
            field=models.ManyToManyField(help_text='Als uw medeonderzoeker niet in de lijst voorkomt, vraag hem dan een keer in te loggen in het webportaal.', related_name='applicants', verbose_name='Uitvoerende(n)', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Intervention',
        ),
    ]
