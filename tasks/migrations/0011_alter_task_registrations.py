# Generated by Django 3.2.13 on 2022-08-26 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0010_auto_20211213_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='registrations',
            field=models.ManyToManyField(help_text='Help!', to='tasks.Registration', verbose_name='Hoe wordt het gedrag of de toestand van de deelnemer bij deze taak vastgelegd?'),
        ),
    ]
