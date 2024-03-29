# Generated by Django 3.2.13 on 2022-10-18 11:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0041_alter_proposal_funding_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="student_justification",
            field=models.TextField(
                blank=True,
                max_length=500,
                verbose_name="Studenten (die mensgebonden onderzoek uitvoeren binnen hun             studieprogramma) hoeven in principe geen aanvraag in te dienen bij de             FETC-GW. Bespreek met je begeleider of je daadwerkelijk een aanvraag             moet indienen. Als dat niet hoeft kun je nu je aanvraag afbreken.             Als dat wel moet, geef dan hier aan wat de reden is:",
            ),
        ),
    ]
