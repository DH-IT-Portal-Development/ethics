# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0011_auto_20170525_0005"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="inform_local_staff",
            field=models.NullBooleanField(
                default=None,
                verbose_name="<p>U hebt aangegeven dat u gebruik wilt gaan maken van \xe9\xe9n van de faciliteiten van het UiL OTS, namelijk de database, Zep software en/of het UiL OTS lab. Het lab supportteam van het UiL OTS zou graag op de hoogte willen worden gesteld van aankomende studies. Daarom vragen wij hier u toestemming om delen van deze aanvraag door te sturen naar het lab supportteam.</p> <p>Vindt u het goed dat de volgende delen uit de aanvraag worden doorgestuurd:</p> - Uw naam en de namen van de andere betrokkenen <br/> - De eindverantwoordelijke van de studie <br/> - De titel van de studie <br/> - De beoogde startdatum <br/> - Van welke faciliteiten u gebruik wilt maken (database, lab, Zep software)",
            ),
        ),
    ]
