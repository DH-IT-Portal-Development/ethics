# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0015_auto_20160422_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='deception',
            field=models.CharField(default=1, choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')], max_length=1, blank=True, help_text='Wellicht ten overvloede: het gaat hierbij niet om fillers.', verbose_name='Is er binnen bovenstaand onderzoekstraject sprake van misleiding van de deelnemer, d.w.z. het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie? Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere deelnemers wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='study',
            name='necessity',
            field=models.CharField(default=1, choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')], max_length=1, blank=True, help_text='Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen deelnemers te testen?', verbose_name='Is het, om de onderzoeksvraag beantwoord te krijgen, noodzakelijk om het geselecteerde type deelnemer aan de studie te laten meedoen?'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='study',
            name='risk',
            field=models.CharField(default=1, choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')], max_length=1, blank=True, help_text='Het achtergrondrisico voor psychische en fysieke schade omvat bijvoorbeeld ook de risico\'s van "routine"-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-<em>assessment</em>, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles, waar relevant, onder begeleiding van adequaat geschoolde specialisten).', verbose_name='Zijn de risico\'s op psychische, fysieke, of andere (bijv. economische, juridische) schade door deelname aan bovenstaand onderzoekstraject <em>meer dan</em> minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke schade bij de deelnemers duidelijk <em>boven</em> het "achtergrondrisico"? Achtergrondrisico is datgene dat gezonde, gemiddelde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt. Ga bij het beantwoorden van deze vraag uit van het naar verwachting meest kwetsbare c.q. minst belastbare (bijv. jongste) geselecteerde deelnemerstype dat dit traject doorloopt. En denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, economische schade door data-koppeling, et cetera.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='study',
            name='stressful',
            field=models.CharField(default=1, choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')], max_length=1, blank=True, help_text="Dit zou bijvoorbeeld het geval kunnen zijn bij een 'onmenselijk' lange en uitputtende taak, een zeer confronterende vragenlijst, of voortdurend vernietigende feedback, maar ook bij een ervaren inbreuk op de privacy, of een ander ervaren gebrek aan respect. Let op, het gaat bij deze vraag om de door de deelnemer ervaren belasting tijdens het onderzoek, niet om de opgelopen psychische of fysieke schade door het onderzoek.", verbose_name='Is bovenstaand onderzoekstraject op onderdelen of als geheel zodanig belastend dat deze <em>ondanks de verkregen informed consent</em> vragen zou kunnen oproepen (of zelfs verontwaardiging), bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers? Ga bij het beantwoorden van deze vraag uit van het naar verwachting meest kwetsbare c.q. minst belastbare (bijv. jongste) geselecteerde deelnemerstype dat dit traject doorloopt.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='study',
            name='surveys_stressful',
            field=models.CharField(default=1, max_length=1, verbose_name='Is het invullen van deze vragenlijsten belastend? Denk hierbij bijv. aan het type vragen dat gesteld wordt en aan de tijd die de persoon kwijt is met het invullen van alle vragenlijsten.', blank=True, choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')]),
            preserve_default=False,
        ),
    ]
