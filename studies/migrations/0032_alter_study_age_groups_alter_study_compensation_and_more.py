# Generated by Django 4.2.11 on 2024-12-18 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("studies", "0031_alter_study_has_sessions_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="study",
            name="age_groups",
            field=models.ManyToManyField(
                help_text="Voorbeeld: Stel dat de beoogde leeftijdsgroep bestaat uit 5–7 jarigen. Dan moet je hier hier 4–5 én 6–11 aanvinken.",
                to="studies.agegroup",
                verbose_name="Uit welke leeftijdscategorie(ën) bestaat je deelnemersgroep?",
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="compensation",
            field=models.ForeignKey(
                blank=True,
                help_text="Het standaardbedrag voor vergoeding aan de deelnemers is €10,- per uur. Minderjarigen mogen geen geld ontvangen, maar wel een cadeautje.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="studies.compensation",
                verbose_name="Welke vergoeding krijgen deelnemers voor hun deelname?",
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="has_special_details",
            field=models.BooleanField(
                blank=True,
                help_text="Wat 'bijzondere of gevoelige persoonsgegevens' zijn kun je vinden op <a href='https://utrechtuniversity.github.io/dataprivacyhandbook/special-types-personal-data.html#special-types-personal-data' target='_blank'>deze pagina</a> van het UU Data Privacy Handbook.",
                null=True,
                verbose_name="Worden er bijzondere of gevoelige persoonsgegevens verzameld of gebruikt?",
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="hierarchy",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Bestaat er een hiërarchische relatie tussen onderzoeker(s) en deelnemer(s) of zouden deelnemers die relatie als hiërarchisch kunnen ervaren?",
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="legal_basis",
            field=models.PositiveIntegerField(
                blank=True,
                choices=[
                    (0, "Dit traject is volledig anoniem."),
                    (1, "De AVG grondslag is 'algemeen belang'."),
                    (2, "De AVG grondslag is 'toestemming'."),
                ],
                help_text="Voor meer informatie over welke AVG grondslag op jouw onderzoek van toepassing is, zie de flowchart in het <a href='https://utrechtuniversity.github.io/dataprivacyhandbook/choose-legal-basis.html' target='_blank'>UU Data Privacy Handbook</a>",
                null=True,
                verbose_name="Wat is de AVG grondslag voor het verzamelen van persoonsgegevens?",
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="name",
            field=models.CharField(
                blank=True, max_length=30, verbose_name="Naam traject"
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="special_details",
            field=models.ManyToManyField(
                blank=True,
                to="studies.specialdetail",
                verbose_name="Geef aan welke bijzondere persoonsgegevens worden verzameld of gebruikt:",
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="traits",
            field=models.ManyToManyField(
                blank=True,
                to="studies.trait",
                verbose_name="Selecteer de medische gegevens van je proefpersonen die worden verzameld of gebruikt",
            ),
        ),
    ]