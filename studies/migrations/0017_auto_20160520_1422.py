# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0016_auto_20160510_1446'),
    ]

    operations = [
        migrations.RenameField(
            model_name='survey',
            old_name='minutes',
            new_name='duration',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='survey_url',
        ),
        migrations.AddField(
            model_name='survey',
            name='url',
            field=models.CharField(max_length=200, verbose_name='URL', blank=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='legally_incapable',
            field=models.NullBooleanField(help_text='Wilsonbekwame volwassenen zijn volwassenen die waarvan redelijkerwijs mag worden aangenomen dat ze onvoldoende kunnen inschatten wat hun eventuele deelname allemaal behelst, en/of waarvan anderszins mag worden aangenomen dat informed consent niet goed gerealiseerd kan worden (bijvoorbeeld omdat ze niet goed hun eigen mening kunnen geven). Hier dient in ieder geval altijd informed consent van een relevante vertegenwoordiger te worden verkregen.', verbose_name='Maakt uw studie gebruik van <strong>volwassen</strong> wils<u>on</u>bekwame deelnemers?'),
        ),
    ]
