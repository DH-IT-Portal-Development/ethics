# Generated by Django 4.2.11 on 2024-11-28 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proposals", "0054_proposal_knowledge_security_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="studies_similar",
            field=models.BooleanField(
                blank=True,
                help_text="Daar waar de verschillen klein en qua belasting of risico irrelevant zijn is sprake van in essentie hetzelfde traject, en voldoet één set documenten voor de bijlagen. Denk hierbij aan taakonderzoek waarin de ene groep in taak X de ene helft van een set verhaaltjes te lezen krijgt, en de andere groep in taak X de andere helft. Of aan interventieonderzoek waarin drie vergelijkbare groepen op hetzelfde moment een verschillende interventie-variant krijgen (specificeer dan wel bij de beschrijving van de interventie welke varianten precies gebruikt worden). Let op: als verschillende groepen deelnemers verschillende <i>soorten</i> taken krijgen, dan kan dit niet en zijn dit afzonderlijke trajecten.",
                null=True,
                verbose_name="Kan voor alle deelnemers dezelfde informatiebrief en, indien van           toepassing, dezelfde toestemmingsverklaring gebruikt worden?",
            ),
        ),
        migrations.AlterField(
            model_name="proposal",
            name="translated_forms",
            field=models.BooleanField(
                blank=True,
                default=None,
                null=True,
                verbose_name="Worden de documenten nog vertaald naar een andere taal dan Nederlands of Engels?",
            ),
        ),
    ]
