# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0005_auto_20160211_2130'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['order']},
        ),
        migrations.AlterField(
            model_name='study',
            name='risk',
            field=models.NullBooleanField(default=False, help_text='Denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, et cetera. Het achtergrondrisico omvat bijvoorbeeld ook de risico\'s van "routine"-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-<em>assessment</em>, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles, waar relevant, onder begeleiding van adequaat geschoolde specialisten).', verbose_name='Zijn de risico\'s op psychische of fysieke schade bij deelname aan de studie <em>meer dan</em> minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke fysieke of psychische schade bij de deelnemers duidelijk <em>boven</em> het "achtergrondrisico"? Achtergrondrisico is datgene dat gezonde, gemiddelde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt. Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep in uw studie.'),
        ),
        migrations.AlterField(
            model_name='study',
            name='stressful',
            field=models.NullBooleanField(default=False, help_text="Dit zou bijvoorbeeld het geval kunnen zijn bij een 'onmenselijk' lange en uitputtende taak, een zeer confronterende vragenlijst, of voortdurend vernietigende feedback, maar ook bij een ervaren inbreuk op de privacy, of een ander ervaren gebrek aan respect. Let op, het gaat bij deze vraag om de door de deelnemer ervaren belasting tijdens het onderzoek, niet om de opgelopen psychische of fysieke schade door het onderzoek.", verbose_name='Is de studie op onderdelen of als geheel zodanig belastend dat deze <em>ondanks de verkregen informed consent </em> vragen zou kunnen oproepen (of zelfs verontwaardiging), bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers? Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep, en neem ook de leeftijd van de deelnemers in deze inschatting mee.'),
        ),
        migrations.AlterField(
            model_name='study',
            name='stressful_details',
            field=models.TextField(verbose_name='Licht je antwoord toe. Geef concrete voorbeelden van de relevante aspecten van uw studie (bijv. representatieve voorbeelden van mogelijk zeer kwetsende woorden of uitspraken in de taak, of van zeer confronterende vragen in een vragenlijst), zodat de commissie zich een goed beeld kan vormen.', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([('session', 'order')]),
        ),
    ]
