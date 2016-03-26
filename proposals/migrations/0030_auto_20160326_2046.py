# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0029_auto_20160326_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='has_traits',
            field=models.BooleanField(verbose_name='Deelnemers kunnen ge\xefncludeerd worden op bepaalde bijzondere kenmerken. Is dit in uw studie bij (een deel van) de deelnemers het geval?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='legally_incapable',
            field=models.BooleanField(verbose_name='Maakt uw studie gebruik van <strong>volwassen</strong> wilsonbekwame deelnemers?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='risk',
            field=models.NullBooleanField(help_text='Het achtergrondrisico voor psychische en fysieke schade omvat bijvoorbeeld ook de risico\'s van "routine"-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-<em>assessment</em>, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles, waar relevant, onder begeleiding van adequaat geschoolde specialisten).', verbose_name='Zijn de risico\'s op psychische, fysieke, of andere (bijv. economische, juridische) schade door deelname aan de studie <em>meer dan</em> minimaal? minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke schade bij de deelnemers duidelijk <em>boven</em> het "achtergrondrisico"? Achtergrondrisico is datgene dat gezonde, gemiddelde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt. Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep in uw studie. En denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, economische schade door data-koppeling, et cetera.'),
        ),
        migrations.AlterField(
            model_name='study',
            name='stressful',
            field=models.NullBooleanField(help_text="Dit zou bijvoorbeeld het geval kunnen zijn bij een 'onmenselijk' lange en uitputtende taak, een zeer confronterende vragenlijst, of voortdurend vernietigende feedback, maar ook bij een ervaren inbreuk op de privacy, of een ander ervaren gebrek aan respect. Let op, het gaat bij deze vraag om de door de deelnemer ervaren belasting tijdens het onderzoek, niet om de opgelopen psychische of fysieke schade door het onderzoek.", verbose_name='Is de studie op onderdelen of als geheel zodanig belastend dat deze <em>ondanks de verkregen informed consent </em> vragen zou kunnen oproepen (of zelfs verontwaardiging), bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers? Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep, en neem ook de leeftijd van de deelnemers in deze inschatting mee.'),
        ),
    ]
