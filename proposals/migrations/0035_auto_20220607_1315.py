# Generated by Django 3.2.13 on 2022-06-07 11:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('proposals', '0034_auto_20211213_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='studies_similar',
            field=models.BooleanField(blank=True, help_text='Daar waar de verschillen klein en qua belasting of risico irrelevant zijn is sprake van in essentie hetzelfde traject. Denk hierbij aan taakonderzoek waarin de ene groep in taak X de ene helft van een set verhaaltjes te lezen krijgt, en de andere groep in taak X de andere helft. Of aan interventieonderzoek waarin drie vergelijkbare groepen op hetzelfde moment een verschillende interventie-variant krijgen (specificeer dan wel bij de beschrijving van de interventie welke varianten precies gebruikt worden). Let op: als verschillende groepen deelnemers verschillende <i>soorten</i> taken krijgen, dan zijn dit verschillende trajecten.', null=True, verbose_name='Doorlopen alle deelnemersgroepen in essentie hetzelfde traject?'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='supervisor',
            field=models.ForeignKey(blank=True, help_text='Aan het einde van de procedure kan je deze aanvraag ter\n        verificatie naar je eindverantwoordelijke sturen. De\n        eindverantwoordelijke zal de aanvraag vervolgens kunnen aanpassen en\n        indienen bij de FETC-GW. <br><br><strong>NB</strong>: als je je\n        eindverantwoordelijke niet kunt vinden met dit veld, moeten zij\n        waarschijnlijk eerst één keer inloggen in deze portal. Je kunt nog wel\n        verder met de aanvraag, maar vergeet dit veld niet in te vullen voor je de\n        aanvraag indient.', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Eindverantwoordelijke onderzoeker'),
        ),
    ]
