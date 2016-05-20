# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0012_auto_20160510_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='applicants',
            field=models.ManyToManyField(help_text='Als uw medeonderzoeker niet in de lijst voorkomt, vraag hem dan een keer in te loggen in het webportaal.', related_name='applicants', verbose_name='Uitvoerende(n) (inclusief uzelf)', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, 'Concept'), (40, 'Opgestuurd ter beoordeling door eindverantwoordelijke'), (50, 'Opgestuurd ter beoordeling door ETCL'), (55, 'Studie is beoordeeld door ETCL'), (60, 'Studie is beoordeeld door METC')]),
        ),
    ]
