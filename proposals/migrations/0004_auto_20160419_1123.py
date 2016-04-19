# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0003_auto_20160401_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='date_start',
            field=models.DateField(null=True, verbose_name='Wat is, indien bekend, de beoogde startdatum van uw studie?', blank=True),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='has_multiple_trajectories',
            field=models.NullBooleanField(help_text='Daar waar de verschillen klein en qua belasting of risico irrelevant zijn is sprake van in essentie hetzelfde traject. Denk hierbij aan taakonderzoek waarin de ene groep in taak X de ene helft van een set verhaaltjes te lezen krijgt, en de andere groep in taak X de andere helft. Of aan interventieonderzoek waarin drie vergelijkbare groepen op hetzelfde moment een verschillende interventie-variant krijgen (specificeer dan wel bij de beschrijving van de interventie welke varianten precies gebruikt worden).', verbose_name='Doorlopen alle deelnemersgroepen in essentie hetzelfde traject?'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='other_applicants',
            field=models.BooleanField(default=False, verbose_name='Zijn er nog andere UiL OTS-onderzoekers of -studenten bij deze studie betrokken?'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='relation',
            field=models.ForeignKey(verbose_name='In welke hoedanigheid bent u betrokken bij deze UiL OTS studie?', to='proposals.Relation'),
        ),
    ]
