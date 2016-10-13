# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faqs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='faq',
            name='answer_en',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='faq',
            name='answer_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='faq',
            name='question_en',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='faq',
            name='question_nl',
            field=models.TextField(null=True),
        ),
    ]
