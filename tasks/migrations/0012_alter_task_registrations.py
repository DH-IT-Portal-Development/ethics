# Generated by Django 3.2.13 on 2022-09-07 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_alter_task_registrations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='registrations',
            field=models.ManyToManyField(help_text="Opnames zijn nooit anoniem en niet te anonimiseren. Let hierop bij het gebruik van de term         ‘anoniem’ of ‘geanonimiseerd’ in je documenten voor deelnemers. Voor meer informatie, zie de         <a href='https://fetc-gw.wp.hum.uu.nl/wp-content/uploads/sites/336/2021/12/FETC-GW-Richtlijnen-voor-geinformeerde-toestemming-bij-wetenschappelijk-onderzoek-versie-1.1_21dec2021.pdf'>         Richtlijnen voor geïnformeerde toestemming, ‘Beeld en geluid’</a>.", to='tasks.Registration', verbose_name='Hoe wordt het gedrag of de toestand van de deelnemer bij deze taak vastgelegd?'),
        ),
    ]
