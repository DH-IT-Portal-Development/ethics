# Generated by Django 3.2.13 on 2022-08-30 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0037_rename_self_assesment_proposal_self_assessment'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='student_program',
            field=models.CharField(blank=True, max_length=200, verbose_name='Wat is je studierichting?'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='studies_similar',
            field=models.BooleanField(blank=True, help_text='Daar waar de verschillen klein en qua belasting of risico irrelevant zijn is sprake van in essentie hetzelfde traject, en voldoet één set documenten voor de informed consent. Denk hierbij aan taakonderzoek waarin de ene groep in taak X de ene helft van een set verhaaltjes te lezen krijgt, en de andere groep in taak X de andere helft. Of aan interventieonderzoek waarin drie vergelijkbare groepen op hetzelfde moment een verschillende interventie-variant krijgen (specificeer dan wel bij de beschrijving van de interventie welke varianten precies gebruikt worden). Let op: als verschillende groepen deelnemers verschillende <i>soorten</i> taken krijgen, dan kan dit niet en zijn dit afzonderlijke trajecten.', null=True, verbose_name='Kan voor alle deelnemersgroepen dezelfde informatiebrief en         toestemmingsverklaring gebruikt worden?'),
        ),
    ]
