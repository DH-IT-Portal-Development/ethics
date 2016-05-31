# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0018_auto_20160528_2247'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='negativity',
            field=models.CharField(blank=True, max_length=1, verbose_name='Bevat bovenstaand onderzoekstraject elementen die <em>tijdens</em> de deelname niet-triviale negatieve emoties kunnen opwekken? Denk hierbij bijvoorbeeld aan emotioneel indringende vragen, kwetsende uitspraken, negatieve feedback, frustrerende, zware, (heel) lange en/of (heel) saaie taken.', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')]),
        ),
        migrations.AddField(
            model_name='study',
            name='negativity_details',
            field=models.TextField(verbose_name='Licht je antwoord toe.', blank=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='age_groups',
            field=models.ManyToManyField(help_text='De beoogde leeftijdsgroep kan zijn 5-7 jarigen. Dan moet u hier hier 4-5 \xe9n 6-11 invullen.', to='studies.AgeGroup', verbose_name='Uit welke leeftijdscategorie(\xebn) bestaat uw deelnemersgroep?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='compensation',
            field=models.ForeignKey(verbose_name='Welke vergoeding krijgt de deelnemer voor zijn/haar deelname?', to='studies.Compensation', help_text='Het standaard bedrag voor vergoeding aan de deelnemers is \u20ac10,- per uur. Minderjarigen mogen geen geld ontvangen, maar wel een cadeautje.', null=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='legally_incapable',
            field=models.NullBooleanField(help_text='Wilsonbekwame volwassenen zijn volwassenen die waarvan redelijkerwijs mag worden aangenomen dat ze onvoldoende kunnen inschatten wat hun eventuele deelname allemaal behelst, en/of waarvan anderszins mag worden aangenomen dat informed consent niet goed gerealiseerd kan worden (bijvoorbeeld omdat ze niet goed hun eigen mening kunnen geven). Hier dient in ieder geval altijd informed consent van een relevante vertegenwoordiger te worden verkregen.', verbose_name='Maakt uw studie gebruik van wils<u>on</u>bekwame (volwassen) deelnemers?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='risk',
            field=models.CharField(blank=True, help_text='Achtergrondrisico is datgene dat gezonde, gemiddelde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt. Denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, economische schade door data-koppeling, et cetera. Het achtergrondrisico voor psychische en fysieke schade omvat bijvoorbeeld ook de risico\'s van "routine"-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-<em>assessment</em>, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles, waar relevant, onder begeleiding van adequaat geschoolde specialisten).', max_length=1, verbose_name='Zijn de risico\'s op psychische, fysieke, of andere (bijv. economische, juridische) schade door deelname aan bovenstaand onderzoekstraject <em>meer dan</em> minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke schade bij de deelnemers duidelijk <em>boven</em> het "achtergrondrisico"?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')]),
        ),
        migrations.AlterField(
            model_name='study',
            name='stressful',
            field=models.CharField(blank=True, help_text="Dit zou bijvoorbeeld het geval kunnen zijn bij een 'onmenselijk' lange en uitputtende taak, een zeer confronterende vragenlijst, of voortdurend vernietigende feedback, maar ook bij een ervaren inbreuk op de privacy, of een ander ervaren gebrek aan respect. Let op, het gaat bij deze vraag om de door de deelnemer ervaren belasting tijdens het onderzoek, niet om de opgelopen psychische of fysieke schade door het onderzoek.", max_length=1, verbose_name='Bevat bovenstaand onderzoekstraject elementen die tijdens de deelname zodanig belastend zijn dat deze <em>ondanks de verkregen informed consent</em> vragen zou kunnen oproepen (of zelfs verontwaardiging), bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')]),
        ),
    ]
