# Generated by Django 2.2.18 on 2021-05-28 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_systemmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemmessage',
            name='message_en',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='systemmessage',
            name='message_nl',
            field=models.CharField(max_length=200, null=True),
        ),
    ]