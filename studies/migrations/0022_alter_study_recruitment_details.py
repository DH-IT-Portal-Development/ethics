# Generated by Django 3.2.13 on 2022-08-26 12:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0021_remove_study_self_assesment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="study",
            name="recruitment_details",
            field=models.TextField(
                blank=True,
                help_text='Er zijn specifieke voorbeelddocumenten voor het gebruik van             Amazon Mechanical Turk/Prolific op <a href="https://intranet.uu.nl/en/knowledgebase/documents-ethics-assessment-committee-humanities">deze pagina</a>.',
                verbose_name="Licht toe",
            ),
        ),
    ]
