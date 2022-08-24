# Generated by Django 3.2.14 on 2022-08-24 13:59

from django.db import migrations, models
import reviews.models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0012_auto_20211213_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='review_type',
            field=models.CharField(choices=[('supervisor', 'Beoordeling door eindverantwoordelijke'), ('committee', 'Beoordeling door commissie')], default=reviews.models.get_default_review_type, max_length=50, verbose_name='Soort beoordeling'),
        ),
    ]
