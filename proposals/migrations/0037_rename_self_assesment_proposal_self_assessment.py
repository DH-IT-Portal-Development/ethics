# Generated by Django 3.2.13 on 2022-07-06 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0036_proposal_self_assesment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proposal',
            old_name='self_assesment',
            new_name='self_assessment',
        ),
    ]