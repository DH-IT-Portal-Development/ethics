# Generated by Django 4.2.11 on 2024-12-05 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proposals", "0055_alter_proposal_other_applicants_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="other_applicants",
            field=models.BooleanField(
                default=None,
                help_text='Werk je samen met een onderzoeker of organisatie buiten de UU en is je onderzoek niet strikt anoniem? Neem dan contact op met de <a href="mailto:privacy.gw@uu.nl">privacy officer</a>. Er moeten dan wellicht afspraken worden gemaakt over de verwerking van persoonsgegevens.',
                null=True,
                verbose_name="Zijn er nog andere onderzoekers bij deze aanvraag betrokken die geaffilieerd zijn aan één van de onderzoeksinstituten ICON, OFR, OGK of ILS?",
            ),
        ),
        migrations.AlterField(
            model_name="proposal",
            name="other_stakeholders",
            field=models.BooleanField(
                default=None,
                null=True,
                verbose_name="Zijn er nog andere onderzoekers bij deze aanvraag betrokken die <strong>niet</strong> geaffilieerd zijn aan een van de onderzoeksinstituten van de Faculteit Geestwetenschappen van de UU? Zoja, vermeld diens naam en affiliatie.",
            ),
        ),
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
