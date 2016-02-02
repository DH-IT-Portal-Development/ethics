# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0011_study_surveys_stressful'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='allow_in_archive',
            field=models.BooleanField(default=True, help_text='Dit archief is alleen toegankelijk voor mensen die aan het UiL OTS geaffilieerd zijn.', verbose_name='Mag deze aanvraag ter goedkeuring in het semi-publiekelijk archief?'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='parent',
            field=models.ForeignKey(verbose_name='Te kopi\xebren aanvraag', to='proposals.Proposal', help_text='Dit veld toont enkel aanvragen waar u zelf een medeaanvrager bent.', null=True),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='sessions_duration',
            field=models.PositiveIntegerField(help_text='Dit is de geschatte totale bruto tijd die de proefpersoon kwijt is aan alle sessie bij elkaar opgeteld, exclusief reistijd.', null=True, verbose_name='De totale geschatte nettoduur komt op basis van uw opgave per sessie uit op <strong>%d minuten</strong>. Wat is de totale duur van de studie? Dus hoeveel tijd zijn de proefpersonen in totaal kwijt door mee te doen aan deze studie?'),
        ),
        migrations.AlterField(
            model_name='session',
            name='deception',
            field=models.NullBooleanField(help_text='Misleiding volgens de definitie van... TODO', verbose_name='Is er binnen deze sessie sprake van misleiding van de proefpersoon, d.w.z. het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie? Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere proefpersonen wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback.'),
        ),
    ]
