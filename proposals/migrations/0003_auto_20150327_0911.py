# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0002_auto_20150317_0802'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='informed_consent_pdf',
            field=models.FileField(upload_to=b'', verbose_name=b'Upload hier de informed consent', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='action',
            name='order',
            field=models.PositiveIntegerField(unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='faq',
            name='order',
            field=models.PositiveIntegerField(unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, b'draft'), (2, b'wmo_awaiting_decision'), (3, b'wmo_finished'), (4, b'study'), (5, b'tasks'), (6, b'informed_consent_uploaded'), (7, b'submitted')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='recruitment',
            name='order',
            field=models.PositiveIntegerField(unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='order',
            field=models.PositiveIntegerField(unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='setting',
            name='order',
            field=models.PositiveIntegerField(unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='actions',
            field=models.ManyToManyField(to='proposals.Action', verbose_name=b'Geef aan welke handeling de proefpersoon moet uitvoeren of aan welke gedragsregel de proefpersoon wordt onderworpen'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='registrations',
            field=models.ManyToManyField(to='proposals.Registration', verbose_name=b'Hoe worden de gegevens vastgelegd? Door middel van:'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='registrations_details',
            field=models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trait',
            name='order',
            field=models.PositiveIntegerField(unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc_decision_pdf',
            field=models.FileField(upload_to=b'', verbose_name=b'Upload hier de beslissing van het METC', blank=True),
            preserve_default=True,
        ),
    ]
