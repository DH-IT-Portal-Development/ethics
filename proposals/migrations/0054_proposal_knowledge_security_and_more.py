# Generated by Django 4.2.11 on 2024-09-24 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proposals", "0053_auto_20240201_1557"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="knowledge_security",
            field=models.CharField(
                blank=True,
                choices=[("Y", "ja"), ("N", "nee"), ("?", "twijfel")],
                help_text="Kennisveiligheid gaat over het tijdig signaleren en mitigeren van veiligheidsrisico's bij wetenschappelijk onderzoek. Klik <a href='https://intranet.uu.nl/kennisbank/kennisveiligheid'>hier</a> voor meer informatie.",
                max_length=1,
                verbose_name="Zijn er kwesties rondom kennisveiligheid?",
            ),
        ),
        migrations.AddField(
            model_name="proposal",
            name="knowledge_security_details",
            field=models.TextField(
                blank=True, max_length=200, verbose_name="Licht toe"
            ),
        ),
        migrations.AddField(
            model_name="proposal",
            name="researcher_risk",
            field=models.CharField(
                blank=True,
                choices=[("Y", "ja"), ("N", "nee"), ("?", "twijfel")],
                help_text="Houd hierbij niet alleen rekening met mogelijke psychische of fysieke schade, maar ook met andere mogelijke schade, zoals bijv. hiërarchische machtsverhoudingen in veldwerk, mogelijke negatieve gevolgen voor de zichtbaarheid/vindbaarheid van de onderzoeker in in het publieke domein, juridische vervolging of aansprakelijkheid, e.d.",
                max_length=1,
                verbose_name="Zijn er kwesties rondom de veiligheid van of risico's voor de onderzoeker(s)?",
            ),
        ),
        migrations.AddField(
            model_name="proposal",
            name="researcher_risk_details",
            field=models.TextField(
                blank=True, max_length=200, verbose_name="Licht toe"
            ),
        ),
    ]
