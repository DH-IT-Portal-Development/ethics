# Generated by Django 4.2.11 on 2024-12-12 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0017_registration_is_recording_alter_task_registrations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session",
            name="tasks_duration",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="De totale geschatte netto taakduur van je sessie komt op basis van je opgave per taak uit op <strong>%d minuten</strong>. Hoeveel minuten duurt de totale sessie, inclusief ontvangst, instructies per taak, pauzes tussen taken, en debriefing? (bij labbezoek dus van binnenkomst tot vertrek en bij een focus-groep van ontvangst tot afsluiting)",
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="description",
            field=models.TextField(
                blank=True,
                verbose_name="Beschrijf de taak die de deelnemer moet uitvoeren, en leg kort uit hoe deze taak (en de eventuele manipulaties daarbinnen) aan de beantwoording van jouw onderzoeksvragen bijdraagt. Geef, kort, een paar voorbeelden (of beschrijvingen) van het type stimuli of prompts dat je van plan bent aan de deelnemer aan te bieden. Het moet voor de commissieleden duidelijk zijn wat je precies gaat doen.",
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="feedback",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Krijgen deelnemers tijdens of na deze taak feedback op hun gedrag of toestand?",
            ),
        ),
    ]
