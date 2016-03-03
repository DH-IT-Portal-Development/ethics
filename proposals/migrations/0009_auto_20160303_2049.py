# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0008_registrationkind_requires_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='allow_in_archive',
            field=models.BooleanField(default=True, help_text='Dit archief is alleen toegankelijk voor mensen die aan het UiL OTS geaffilieerd zijn.', verbose_name='Mag deze studie ter goedkeuring in het semi-publiekelijk archief?'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='parent',
            field=models.ForeignKey(verbose_name='Te kopi\xebren studie', to='proposals.Proposal', help_text='Dit veld toont enkel studies waar u zelf een medeuitvoerende bent.', null=True),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, 'Algemene informatie ingevuld'), (2, 'WMO: geen beoordeling door METC noodzakelijk'), (3, 'WMO: wordt beoordeeld door METC'), (4, 'Kenmerken studie toegevoegd'), (5, 'Belasting deelnemer: sessies toevoegen'), (6, 'Belasting deelnemer: taken toevoegen'), (7, 'Belasting deelnemer: alle taken toegevoegd'), (8, 'Belasting deelnemer: afgerond'), (9, 'Belasting deelnemer: afgerond'), (10, 'Informed consent ge\xfcpload'), (40, 'Opgestuurd ter beoordeling door eindverantwoordelijke'), (50, 'Opgestuurd ter beoordeling door ETCL'), (55, 'Studie is beoordeeld door ETCL'), (60, 'Studie is beoordeeld door METC')]),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='supervisor',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text='Aan het einde van de procedure kunt u deze studie ter verificatie naar uw eindverantwoordelijke sturen. De eindverantwoordelijke zal de studie vervolgens kunnen aanpassen en indienen bij de ETCL.', null=True, verbose_name='Eindverantwoordelijke onderzoeker'),
        ),
        migrations.AlterField(
            model_name='study',
            name='risk',
            field=models.NullBooleanField(default=False, help_text='Het achtergrondrisico voor psychische en fysieke schade omvat bijvoorbeeld ook de risico\'s van "routine"-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-<em>assessment</em>, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles, waar relevant, onder begeleiding van adequaat geschoolde specialisten).', verbose_name='Zijn de risico\'s op psychische, fysieke, of andere (bijv. economische, juridische) schade door deelname aan de studie <em>meer dan</em> minimaal? minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke schade bij de deelnemers duidelijk <em>boven</em> het "achtergrondrisico"? Achtergrondrisico is datgene dat gezonde, gemiddelde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt. Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep in uw studie. En denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, economische schade door data-koppeling, et cetera.'),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc_application',
            field=models.BooleanField(default=False, verbose_name='Uw studie moet beoordeeld worden door de METC, maar dient nog wel bij de ETCL te worden geregistreerd. Is voor deze studie al aangemeld bij een METC?'),
        ),
    ]
