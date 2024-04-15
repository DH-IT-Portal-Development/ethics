from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class YesNoDoubt(models.TextChoices):
    YES = "Y", _("ja")
    NO = "N", _("nee")
    DOUBT = "?", _("twijfel")


class SystemMessage(models.Model):
    class Levels(models.IntegerChoices):
        # Not translated, as it's backend only
        URGENT = 1, "Urgent"
        ATTENTION = 2, "Attention"
        INFO = 3, "Info"

    message = models.TextField()
    level = models.IntegerField(choices=Levels.choices)
    not_before = models.DateTimeField()
    not_after = models.DateTimeField()

    @property
    def css_class(self):
        if self.level == self.Levels.URGENT:
            return "failed"
        if self.level == self.Levels.ATTENTION:
            return "warning"
        if self.level == self.Levels.INFO:
            return "info"

        return ""


class Setting(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    is_local = models.BooleanField(default=False)
    needs_details = models.BooleanField(default=False)
    needs_supervision = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    # Variable is called is_school because in the early requirement it was
    # only in schools. Now it's been extended and thus renamed.
    is_school = models.BooleanField("Needs external permission", default=False)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Setting")

    def __str__(self):
        return self.description


class SettingModel(models.Model):
    setting = models.ManyToManyField(
        Setting,
        verbose_name=_("Geef aan waar de dataverzameling plaatsvindt"),
        blank=True,  # TODO: mark this as soft required in ALL forms
    )
    setting_details = models.CharField(
        _("Namelijk"),
        max_length=200,
        blank=True,
    )
    supervision = models.BooleanField(
        _(
            "Vindt het afnemen van de taak plaats onder het toeziend oog \
van de leraar of een ander persoon die bevoegd is?"
        ),
        null=True,
        blank=True,
    )
    leader_has_coc = models.BooleanField(
        _("Is de testleider in het bezit van een VOG?"),
        help_text=_(
            'Iedereen die op een school werkt moet in het bezit \
        zijn van een Verklaring Omtrent Gedrag (VOG, zie \
        <a href="https://www.justis.nl/producten/vog/" \
        target="_blank">https://www.justis.nl/producten/vog/</a>). \
        Het is de verantwoordelijkheid van de school om hierom te vragen. \
        De FETC-GW neemt hierin een adviserende rol en wil de onderzoekers \
        waarschuwen dat de school om een VOG kan vragen.'
        ),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def settings_contains_schools(self):
        """If the current settings contains any that are marked as schools."""
        return self.setting.filter(is_school=True).exists()

    def settings_requires_review(self):
        """If the current settings contain any that requires review"""
        return self.setting.filter(requires_review=True)


class Faculty(models.Model):
    class InternalNames(models.TextChoices):
        HUMANITIES = "humanities"
        OTHER = "other"

    name = models.CharField(max_length=255)

    # This should be the same as the Dutch name, but we store it separately
    # to allow us to edit `name` freely
    saml_name = models.CharField(
        max_length=255,
    )

    users = models.ManyToManyField(get_user_model(), related_name="faculties")

    internal_name = models.CharField(
        max_length=50,
        choices=InternalNames.choices,
        default=InternalNames.OTHER,
    )

    def __str__(self):
        return self.name


class SamlUserProxy(User):
    """This special proxy model is used to process attributes from SAML
    It's not a replacement User model. It may be used elsewhere in code, but
    why would you?
    """

    class Meta:
        proxy = True

    def process_faculties(self, faculties):
        """Receives a list of faculties of the user and couples them to the
        relevant Faculty. Also creates a new Faculty for not-yet-know
        faculties.
        """
        for faculty in faculties:
            # Ignore empty values
            if not faculty:
                continue

            # We should manually maintain some ourselves, but this allows
            # some auto-population
            if not Faculty.objects.filter(saml_name=faculty).exists():
                Faculty.objects.create(
                    saml_name=faculty,
                    name_nl=faculty,  # SAML gives us the Dutch names
                )

            try:
                faculty_obj = Faculty.objects.get(saml_name=faculty)

                # Don't re-add.
                if faculty_obj.users.filter(pk=self.pk).exists():
                    continue

                faculty_obj.users.add(self)
            except:
                # Just ignore any errors...
                continue
