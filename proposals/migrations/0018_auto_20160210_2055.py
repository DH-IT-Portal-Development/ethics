# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0017_auto_20160210_1942'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='registration_kind',
            new_name='registration_kinds',
        ),
        migrations.AddField(
            model_name='registrationkind',
            name='needs_details',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='registration_kinds_details',
            field=models.CharField(max_length=200, verbose_name='Namelijk', blank=True),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='passive_consent',
            field=models.BooleanField(default=False, help_text='Wanneer u kinderen via een instelling (dus ook school) werft en u de ouders niet laat ondertekenen, maar in plaats daarvan de leiding van die instelling, dan maakt u gebruik van passieve informed consent. U kunt de templates vinden op <link website?>', verbose_name='Maakt uw studie gebruik van passieve informed consent?'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='sessions_duration',
            field=models.PositiveIntegerField(help_text='Dit is de geschatte totale bruto tijd die de deelnemer kwijt is aan alle sessies bij elkaar opgeteld, exclusief reistijd.', null=True, verbose_name='De netto duur van uw studie komt op basis van uw opgegeven tijd, uit op <strong>%d minuten</strong>. Wat is de totale duur van de gehele studie? Schat de totale tijd die de deelnemers kwijt zijn aan de studie.'),
        ),
        migrations.AlterField(
            model_name='study',
            name='has_traits',
            field=models.BooleanField(default=False, verbose_name='Deelnemers kunnen ge\xefncludeerd worden op bepaalde bijzondere kenmerken. Is dit in uw studie bij (een deel van) de deelnemers het geval?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='legally_incapable',
            field=models.BooleanField(default=False, verbose_name='Maakt uw studie gebruik van volwassen wilsonbekwame deelnemers?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='necessity',
            field=models.NullBooleanField(help_text='Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen deelnemers te testen?', verbose_name='Is het, om de onderzoeksvraag beantwoord te krijgen, noodzakelijk om het geselecteerde type deelnemer aan de studie te laten meedoen?'),
        ),
        migrations.AlterField(
            model_name='task',
            name='duration',
            field=models.PositiveIntegerField(default=0, verbose_name='Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per deelnemer varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.', validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
