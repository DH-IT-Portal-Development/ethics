from django.db import models
from django.utils.translation import ugettext_lazy as _

YES = 'Y'
NO = 'N'
DOUBT = '?'
YES_NO_DOUBT = (
    (YES, _('ja')),
    (NO, _('nee')),
    (DOUBT, _('twijfel')),
)


class Setting(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    is_local = models.BooleanField(default=False)
    needs_details = models.BooleanField(default=False)
    needs_supervision = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    # Variable is called is_school because in the early requirement it was only in schools. Now it's been extended and thus renamed
    is_school = models.BooleanField("Needs external permission", default=False)

    class Meta:
        ordering = ['order']
        verbose_name = _('Setting')

    def __str__(self):
        return self.description


class SettingModel(models.Model):
    setting = models.ManyToManyField(
        Setting,
        verbose_name=_('Geef aan waar de dataverzameling plaatsvindt'),
        blank=True, # TODO: mark this as soft required in ALL forms
    )
    setting_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True,
    )
    supervision = models.BooleanField(
        _('Vindt het afnemen van de taak plaats onder het toeziend oog \
van de leraar of een ander persoon die bevoegd is?'),
        null=True,
        blank=True,
    )
    leader_has_coc = models.BooleanField(
        _('Is de testleider in het bezit van een VOG?'),
        help_text=_('Iedereen die op een school werkt moet in het bezit \
        zijn van een Verklaring Omtrent Gedrag (VOG, zie \
        <a href="https://www.justis.nl/producten/vog/" \
        target="_blank">https://www.justis.nl/producten/vog/</a>). \
        Het is de verantwoordelijkheid van de school om hierom te vragen. \
        De FETC-GW neemt hierin een adviserende rol en wil de onderzoekers \
        waarschuwen dat de school om een VOG kan vragen.'),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def settings_contains_schools(self):
        """If the current settings contains any that are marked as schools."""
        return self.setting.filter(is_school=True).exists();

    def settings_requires_review(self):
        """If the current settings contain any that requires review"""
        return self.setting.filter(requires_review=True)