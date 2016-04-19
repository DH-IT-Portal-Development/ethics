# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0008_auto_20160419_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='compensation',
            field=models.ForeignKey(verbose_name='Welke vergoeding krijgt de deelnemer voor zijn/haar deelname?', to='studies.Compensation', help_text='tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld', null=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='passive_consent',
            field=models.BooleanField(default=False, help_text='Wanneer u kinderen via een instelling (dus ook school) werft en u de ouders niet laat ondertekenen, maar in plaats daarvan de leiding van die instelling, dan maakt u gebruik van passieve informed consent. U kunt de templates vinden op <link website?>', verbose_name='Maakt u gebruik van passieve informed consent?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='risk',
            field=models.NullBooleanField(help_text='Het achtergrondrisico voor psychische en fysieke schade omvat bijvoorbeeld ook de risico\'s van "routine"-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-<em>assessment</em>, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles, waar relevant, onder begeleiding van adequaat geschoolde specialisten).', verbose_name='Zijn de risico\'s op psychische, fysieke, of andere (bijv. economische, juridische) schade door deelname aan bovenstaand onderzoekstraject <em>meer dan</em> minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke schade bij de deelnemers duidelijk <em>boven</em> het "achtergrondrisico"? Achtergrondrisico is datgene dat gezonde, gemiddelde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt. Ga bij het beantwoorden van deze vraag uit van het naar verwachting meest kwetsbare c.q. minst belastbare (bijv. jongste) geselecteerde deelnemerstype dat dit traject doorloopt. En denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, economische schade door data-koppeling, et cetera.'),
        ),
        migrations.AlterField(
            model_name='study',
            name='stressful',
            field=models.NullBooleanField(help_text="Dit zou bijvoorbeeld het geval kunnen zijn bij een 'onmenselijk' lange en uitputtende taak, een zeer confronterende vragenlijst, of voortdurend vernietigende feedback, maar ook bij een ervaren inbreuk op de privacy, of een ander ervaren gebrek aan respect. Let op, het gaat bij deze vraag om de door de deelnemer ervaren belasting tijdens het onderzoek, niet om de opgelopen psychische of fysieke schade door het onderzoek.", verbose_name='Is bovenstaand onderzoekstraject op onderdelen of als geheel zodanig belastend dat deze <em>ondanks de verkregen informed consent</em> vragen zou kunnen oproepen (of zelfs verontwaardiging), bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers? Ga bij het beantwoorden van deze vraag uit van het naar verwachting meest kwetsbare c.q. minst belastbare (bijv. jongste) geselecteerde deelnemerstype dat dit traject doorloopt.'),
        ),
    ]
