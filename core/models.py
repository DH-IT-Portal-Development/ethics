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

    class Meta:
        ordering = ['order']
        verbose_name = _('Setting')

    def __unicode__(self):
        return self.description


class SettingModel(models.Model):
    setting = models.ManyToManyField(
        Setting,
        verbose_name=_('Geef aan waar de dataverzameling plaatsvindt'))
    setting_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True)
    supervision = models.NullBooleanField(
        _('Vindt het afnemen van de taak plaats onder het toeziend oog \
van de leraar of een ander persoon die bevoegd is?')
    )

    class Meta:
        abstract = True
