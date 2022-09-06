# Generated by Django 3.2.14 on 2022-09-06 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0012_auto_20211213_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='review_type',
            field=models.CharField(choices=[('supervisor', 'Beoordeling door eindverantwoordelijke'), ('committee', 'Beoordeling door commissie')], max_length=50, null=True, verbose_name='Soort beoordeling'),
        ),
    ]
