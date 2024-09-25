# Generated by Django 4.2.11 on 2024-09-25 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studies", "0028_remove_study_sessions_number"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="study",
            name="stressful",
        ),
        migrations.RemoveField(
            model_name="study",
            name="stressful_details",
        ),
        migrations.AlterField(
            model_name="study",
            name="deception",
            field=models.CharField(
                blank=True,
                choices=[("Y", "ja"), ("N", "nee"), ("?", "twijfel")],
                help_text='Misleiding is het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens het onderzoek. Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er door de deelnemer met andere deelnemers wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback. Wellicht ten overvloede: het gaat hierbij niet om fillers in bijv. taalwetenschappelijk onderzoek.',
                max_length=1,
                verbose_name="Is er binnen bovenstaand onderzoekstraject sprake van misleiding van de deelnemer?",
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="negativity",
            field=models.CharField(
                blank=True,
                choices=[("Y", "ja"), ("N", "nee"), ("?", "twijfel")],
                max_length=1,
                verbose_name="Bevat bovenstaand onderzoekstraject elementen die <em>tijdens</em> de deelname zodanig belastend zijn dat deze vragen, weerstand, of zelfs verontwaardiging zouden kunnen oproepen, bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers?",
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="negativity_details",
            field=models.TextField(
                blank=True,
                help_text="Geef concrete voorbeelden van de relevante aspecten van jouw onderzoek (bijv. voorbeelden van mogelijk zeer kwetsende woorden of uitspraken in de taak; zeer confronterende vragen in een vragenlijst; negatieve feedback), zodat de commissie zich een goed beeld kan vormen.",
                verbose_name="Licht toe",
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="risk",
            field=models.CharField(
                blank=True,
                choices=[("Y", "ja"), ("N", "nee"), ("?", "twijfel")],
                help_text="Houd hierbij niet alleen rekening met mogelijke psychische of fysieke schadelijke gevolgen, maar ook met andere mogelijke schade, zoals bijv. stigmatisering, (re-)traumatisering, aantasting van zelfbeeld, verlies van privacy, toevalsbevindingen, juridische vervolging of aansprakelijkheid, e.d.",
                max_length=1,
                verbose_name="Zijn er kwesties rondom de veiligheid van, of risico's voor de deelnemers <em>tijdens of na</em> deelname aan het onderzoek?",
            ),
        ),
    ]
