# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0017_auto_20160520_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='legally_incapable_details',
            field=models.TextField(verbose_name='Licht toe', blank=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='compensation',
            field=models.ForeignKey(verbose_name='Welke vergoeding krijgt de deelnemer voor zijn/haar deelname?', to='studies.Compensation', help_text='Het standaard bedrag voor vergoeding aan de deelnemers is \u20ac10,- per uur. Minderjarigen mogen geen geld ontvangen, maar wel een cadeautje', null=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='deception',
            field=models.CharField(blank=True, help_text='Misleiding is het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie. Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere deelnemers wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback. Wellicht ten overvloede: het gaat hierbij niet om fillers.', max_length=1, verbose_name='Is er binnen bovenstaand onderzoekstraject sprake van misleiding van de deelnemer?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')]),
        ),
        migrations.AlterField(
            model_name='study',
            name='passive_consent',
            field=models.BooleanField(default=False, help_text='Wanneer u kinderen via een instelling (dus ook school) werft en u de ouders niet laat ondertekenen, maar in plaats daarvan de leiding van die instelling, dan maakt u gebruik van passieve informed consent. U kunt de templates vinden op <a href="https://etcl.wp.hum.uu.nl/toestemmingsverklaringen/" target="_blank">de ETCL-website</a>.', verbose_name='Maakt u gebruik van passieve informed consent?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='recruitment_details',
            field=models.TextField(verbose_name='Licht toe', blank=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='risk',
            field=models.CharField(blank=True, help_text='Achtergrondrisico is datgene dat gezonde, gemiddelde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt. Ga bij het beantwoorden van deze vraag uit van het naar verwachting meest kwetsbare c.q. minst belastbare (bijv. jongste) geselecteerde deelnemerstype dat dit traject doorloopt. En denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, economische schade door data-koppeling, et cetera. Het achtergrondrisico voor psychische en fysieke schade omvat bijvoorbeeld ook de risico\'s van "routine"-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-<em>assessment</em>, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles, waar relevant, onder begeleiding van adequaat geschoolde specialisten).', max_length=1, verbose_name='Zijn de risico\'s op psychische, fysieke, of andere (bijv. economische, juridische) schade door deelname aan bovenstaand onderzoekstraject <em>meer dan</em> minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke schade bij de deelnemers duidelijk <em>boven</em> het "achtergrondrisico"?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')]),
        ),
    ]
