# Generated by Django 3.2.20 on 2023-11-16 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0049_alter_proposal_supervisor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='avg_understood',
        ),
        migrations.AddField(
            model_name='proposal',
            name='privacy_officer',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='Ik heb mijn aanvraag en de documenten voor deelnemers besproken met de privacy officer.'),
        ),
    ]
