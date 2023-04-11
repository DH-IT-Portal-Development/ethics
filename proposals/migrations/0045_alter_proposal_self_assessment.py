# Generated by Django 3.2.14 on 2023-04-11 11:22

from django.db import migrations, models
import main.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0044_auto_20221206_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='self_assessment',
            field=models.TextField(blank=True, validators=[main.validators.MaxWordsValidator(300)], verbose_name='Wat zijn de belangrijkste ethische kwesties in dit onderzoek en beschrijf kort hoe ga je daarmee omgaat.  Gebruik maximaal 300 woorden.'),
        ),
    ]
