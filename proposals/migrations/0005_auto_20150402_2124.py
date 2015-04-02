# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('proposals', '0004_auto_20150327_1326'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compensation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_supervisor', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='creator_function',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='name',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='supervisor_name',
        ),
        migrations.RemoveField(
            model_name='study',
            name='surveys',
        ),
        migrations.AddField(
            model_name='proposal',
            name='created_by',
            field=models.ForeignKey(related_name='created_by', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proposal',
            name='other_applicants',
            field=models.BooleanField(default=False, verbose_name=b'Zijn er nog andere UiL OTS-onderzoekers bij deze studie betrokken?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='relation',
            field=models.ManyToManyField(to='proposals.Relation', verbose_name=b'Wat is uw relatie tot het UiL OTS?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='title',
            field=models.CharField(default='test', help_text=b'Kies s.v.p. een titel die niet volledig identiek is aan die van eerder ingediende studies.', max_length=200, verbose_name=b'Titel studie'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='study',
            name='compensation_details',
            field=models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='study',
            name='has_traits',
            field=models.BooleanField(default=False, verbose_name=b'Proefpersonen kunnen geselecteerd worden op bepaalde bijzondere kenmerken die mogelijk samenhangen met een verhoogde kwetsbaarheid of verminderde belastbaarheid t.a.v. aspecten van de beoogde studie (bijvoorbeeld: kinderen die vroeger gepest zijn in een onderzoek naar de neurale reactie op verbale beledigingen; pati&#235;nten met afasie die een gesprek moeten voeren, ook al gaat het gesprek over alledaagse dingen). Is dit in uw studie bij (een deel van) de proefpersonen het geval?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='survey',
            name='study',
            field=models.ForeignKey(default=1, to='proposals.Study'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wmo',
            name='metc_application',
            field=models.BooleanField(default=False, verbose_name=b'Uw studie moet beoordeeld worden door de METC<link>, maar dient nog wel bij de ETCL te worden geregistreerd. Is voor deze studie al een METC aanvraag ingediend?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='longitudinal',
            field=models.BooleanField(default=False, verbose_name=b'Is dit een studie waarbij dezelfde proefpersonen op meerdere dagen aan een sessie deelnemen? (bijvoorbeeld een longitudinale studie, of een kortlopende studie waar proefpersonen op twee of meer verschillende dagen getest worden)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='supervisor_email',
            field=models.EmailField(help_text=b'Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.', max_length=75, verbose_name=b'E-mailadres eindverantwoordelijke', blank=b'True'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='age_groups',
            field=models.ManyToManyField(to='proposals.AgeGroup', verbose_name=b'Geef hieronder aan binnen welke leeftijdscategorie uw proefpersonen vallen, er zijn meerdere antwoorden mogelijk'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='necessity',
            field=models.NullBooleanField(default=True, help_text=b'Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen proefpersonen te testen?', verbose_name=b'Is het om de onderzoeksvraag beantwoord te krijgen noodzakelijk om het geselecteerde type proefpersonen aan de studie te laten deelnemen?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='risk_physical',
            field=models.NullBooleanField(default=False, verbose_name=b'Is de kans dat de proefpersoon fysiek letsel oploopt tijdens het afnemen van het experiment groter dan de kans op letsel in het dagelijks leven?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='risk_psychological',
            field=models.NullBooleanField(default=False, verbose_name=b'Is de kans dat de proefpersoon psychisch letsel oploopt tijdens het afnemen van het experiment groter dan de kans op letsel in het dagelijks leven?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='traits',
            field=models.ManyToManyField(to='proposals.Trait', verbose_name=b'Selecteer de bijzondere kenmerken van uw proefpersonen'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wmo',
            name='is_behavioristic',
            field=models.NullBooleanField(default=False, help_text=b'Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een proefpersoon tot de proefpersoon een knop/toets in laten drukken.', verbose_name=b'Worden de proefpersonen aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wmo',
            name='is_medical',
            field=models.NullBooleanField(default=False, verbose_name=b'Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc',
            field=models.NullBooleanField(default=False, verbose_name=b'Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc_decision',
            field=models.BooleanField(default=False, verbose_name=b'Is de METC al tot een beslissing gekomen?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc_institution',
            field=models.CharField(max_length=200, verbose_name=b'Welke instelling?', blank=True),
            preserve_default=True,
        ),
    ]
