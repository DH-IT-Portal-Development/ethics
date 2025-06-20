# -*- encoding: utf-8 -*-

from xml.dom import HierarchyRequestErr
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q


from django.utils.translation import gettext_lazy as _
from django.utils.functional import lazy
from django.utils.safestring import mark_safe, SafeString

mark_safe_lazy = lazy(mark_safe, SafeString)

from main.models import YesNoDoubt
from main.validators import validate_pdf_or_doc
from proposals.models import Proposal
from proposals.utils.proposal_utils import FilenameFactory, OverwriteStorage
from tasks.models import Task

INFORMED_CONSENT_FILENAME = FilenameFactory("Informed_Consent")
METC_DECISION_FILENAME = FilenameFactory("METC_Decision")
BRIEFING_FILENAME = FilenameFactory("Briefing")
DEPARTMENT_CONSENT_FILENAME = FilenameFactory("Department_Consent")
DEPARTMENT_INFO_FILENAME = FilenameFactory("Department_Info")
PARENTAL_INFO_FILENAME = FilenameFactory("Parental_Info")


class AgeGroup(models.Model):
    """
    A model to store participant age groups.
    The model has fields for the age range, a description and whether this age group is considered adult.
    The 'needs_details' field is used to determine whether the 'necessity' field on Study needs to be filled.
    The 'max_net_duration' field is used in the automatic review to check the target Session duration is not exceeded.
    The 'is_active' field is used for when the age groups need to be redefined. Create new ones for the groups that need
    to be redefined, and set the old ones to inactive. This is needed to preserve old proposals for the archive.
    """

    class Meta:
        ordering = ("age_min",)

    age_min = models.PositiveIntegerField()
    age_max = models.PositiveIntegerField(blank=True, null=True)
    description = models.CharField(max_length=200)
    is_adult = models.BooleanField(default=False)
    needs_details = models.BooleanField(default=False)
    max_net_duration = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.age_max:
            return _("{}-{} jaar").format(self.age_min, self.age_max)
        else:
            return _("{} jaar en ouder").format(self.age_min)


class Trait(models.Model):
    """
    A model to store participant traits.
    The model has fields to keep a certain order and a description.
    The 'needs_details' field is used to determine whether the 'necessity' field on Study needs to be filled.
    This class of traits is now organised as a subquestion of the special_personal_details under the 2022 regulations,
    but Traits have been recorded before we started recording special_personal_details
    """

    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class SpecialDetail(models.Model):
    """ "
    A model to store different 'special details' that are extra sensitive, such as race, sexuality etc.
    """

    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    medical_traits = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class Compensation(models.Model):
    """
    A model to store forms of participant compensation.
    The model has fields to keep a certain order and a description.
    The 'needs_details' field is used to determine whether the 'compensation_details' field on Study needs to be filled.
    The 'requires_review' field is used in the automatic review to tag anomalous forms of compensation.
    """

    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class Recruitment(models.Model):
    """
    A model to store forms of participant recruitment.
    The model has fields to keep a certain order and a description.
    The 'is_local' field is used to determine whether the 'inform_local_staff' field on Proposal needs to be filled.
    The 'needs_details' field is used to determine whether the 'recruitment_details' field on Study needs to be filled.
    The 'requires_review' field is used in the automatic review to tag anomalous forms of recruitment.
    """

    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    is_local = models.BooleanField(default=False)
    needs_details = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Werving")

    def __str__(self):
        return self.description


class Registration(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    is_local = models.BooleanField(default=False)
    needs_details = models.BooleanField(default=False)
    needs_kind = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    age_min = models.PositiveIntegerField(blank=True, null=True)
    is_recording = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["order"]
        verbose_name = _("Vastlegging gedrag")

    def __str__(self):
        return self.description


class RegistrationKind(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class Study(models.Model):
    """
    A model to store a study within a Proposal.
    A Study consists of participant details, experiment design and consent forms.
    """

    class LegalBases(models.IntegerChoices):
        ANONYMOUS = 0, _("Dit traject is volledig anoniem.")
        PUBLIC_INTEREST = 1, _("De AVG grondslag is 'algemeen belang'.")
        CONSENT = 2, _("De AVG grondslag is 'toestemming'.")

    order = models.PositiveIntegerField()
    name = models.CharField(_("Naam traject"), max_length=30, blank=True)

    age_groups = models.ManyToManyField(
        AgeGroup,
        verbose_name=_("Uit welke leeftijdscategorie(ën) bestaat je deelnemersgroep?"),
        help_text=_(
            "Voorbeeld: Stel dat de beoogde leeftijdsgroep bestaat uit 5–7 "
            "jarigen. Dan moet je hier hier 4–5 én 6–11 aanvinken."
        ),
    )
    legally_incapable = models.BooleanField(
        _(
            "Maakt je onderzoek gebruik van wils<u>on</u>bekwame volwassen "
            "deelnemers?"
        ),  # Note: Form labels with HTML are hard-coded in the Form meta class
        help_text=_(
            "Wilsonbekwame volwassenen zijn volwassenen waarvan \
redelijkerwijs mag worden aangenomen dat ze onvoldoende kunnen inschatten \
wat hun eventuele deelname allemaal behelst, en/of waarvan anderszins mag \
worden aangenomen dat bewuste toestemming niet goed gerealiseerd kan worden \
(bijvoorbeeld omdat ze niet goed hun eigen mening kunnen geven). \
Hier dient in ieder geval altijd toestemming van een relevante \
vertegenwoordiger te worden verkregen."
        ),
        default=False,
    )
    legally_incapable_details = models.TextField(_("Licht toe"), blank=True)

    has_special_details = models.BooleanField(
        verbose_name=_(
            "Worden er bijzondere of gevoelige persoonsgegevens verzameld of gebruikt?"
        ),
        help_text=_(
            "Wat 'bijzondere of gevoelige persoonsgegevens' zijn kun je "
            "vinden op <a href='https://utrechtuniversity.github.io/"
            "dataprivacyhandbook/special-types-personal-data.html#special"
            "-types-personal-data' target='_blank'>deze pagina</a> van "
            "het UU Data Privacy Handbook."
        ),
        null=True,
        blank=True,
    )

    legal_basis = models.PositiveIntegerField(
        verbose_name=_(
            "Wat is de AVG grondslag voor het verzamelen van " "persoonsgegevens?"
        ),
        help_text=_(
            "Voor meer informatie over welke AVG grondslag op jouw onderzoek van "
            "toepassing is, zie de flowchart in het "
            "<a href='https://utrechtuniversity.github.io/dataprivacyhandbook/choose-legal-basis.html'"
            " target='_blank'>UU Data Privacy Handbook</a>"
        ),
        choices=LegalBases.choices,
        null=True,
        blank=True,
    )

    special_details = models.ManyToManyField(
        SpecialDetail,
        blank=True,
        verbose_name=_(
            "Geef aan welke bijzondere persoonsgegevens worden verzameld of gebruikt:"
        ),
    )

    has_traits = models.BooleanField(
        _(
            "Deelnemers kunnen geïncludeerd worden op bepaalde bijzondere kenmerken. \
Is dit in jouw onderzoek bij (een deel van) de deelnemers het geval?"
        ),
        help_text=_(
            "In de meeste gevallen kun je dit soort gegevens alleen verzamelen als je \
daar toestemming voor hebt: zie de \
<a href='https://fetc-gw.wp.hum.uu.nl/wp-content/uploads/sites/336/2021/12/FETC-GW-Richtlijnen-voor-geinformeerde-toestemming-bij-wetenschappelijk-onderzoek-versie-1.1_21dec2021.pdf' target='_blank'>Richtlijnen voor geïnformeerde toestemming,</a> \
‘Bijzondere persoonsgegevens’. Is het in de praktijk onmogelijk of \
disproportioneel moeilijk om om toestemming te vragen, neem dan \
eerst contact op met de <a href='mailto:privacy.gw@uu.nl'>privacy officer</a>, voordat je je aanvraag indient."
        ),
        null=True,
        blank=True,
    )
    traits = models.ManyToManyField(
        Trait,
        blank=True,
        verbose_name=_(
            "Selecteer de medische gegevens van je proefpersonen die worden verzameld of gebruikt"
        ),
    )
    traits_details = models.CharField(_("Namelijk"), max_length=200, blank=True)
    necessity = models.CharField(
        _(
            "Is het, om de onderzoeksvraag beantwoord te krijgen, \
noodzakelijk om het geselecteerde type deelnemer aan het onderzoek te \
laten meedoen?"
        ),
        help_text=_(
            "Is het bijvoorbeeld noodzakelijk om kinderen te testen, \
of zou je de vraag ook kunnen beantwoorden door volwassen deelnemers \
te testen?"
        ),
        max_length=1,
        choices=YesNoDoubt.choices,
        blank=True,
    )
    necessity_reason = models.TextField(_("Leg uit waarom"), blank=True)
    recruitment = models.ManyToManyField(
        Recruitment, verbose_name=_("Hoe worden de deelnemers geworven?")
    )
    recruitment_details = models.TextField(
        _("Licht toe"),
        blank=True,
    )
    compensation = models.ForeignKey(
        Compensation,
        verbose_name=_("Welke vergoeding krijgen deelnemers voor hun deelname?"),
        help_text=_(
            "Het standaardbedrag voor vergoeding aan de deelnemers \
is €10,- per uur. Minderjarigen mogen geen geld ontvangen, maar wel een \
cadeautje."
        ),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    compensation_details = models.CharField(_("Namelijk"), max_length=200, blank=True)

    hierarchy = models.BooleanField(
        verbose_name=_(
            "Bestaat er een hiërarchische relatie tussen onderzoeker(s) "
            "en deelnemer(s) of zouden deelnemers die relatie als "
            "hiërarchisch kunnen ervaren?"
        ),
        null=True,
        blank=True,
    )

    hierarchy_details = models.TextField(
        verbose_name=_("Zo ja, wat is de relatie (bijv. docent-student)?"),
        max_length=500,
        blank=True,
    )

    # Fields with regards to registration

    registrations = models.ManyToManyField(
        Registration,
        verbose_name=_(
            "Hoe wordt het gedrag of de toestand van de deelnemer bij deze studie vastgelegd?"
        ),
        help_text=_(
            "Opnames zijn nooit anoniem en niet te anonimiseren. Let hierop "
            "bij het gebruik van de term 'anoniem' of 'geanonimiseerd' in "
            "je documenten voor deelnemers. Voor meer informatie, zie het UU Data Privacy Handbook over "
            "<a href='https://utrechtuniversity.github.io/dataprivacyhandbook/pseudonymisation-anonymisation.html#pseudonymisation-anonymisation' target='_blank'>"
            "anonimiseren en pseudonimiseren</a>."
        ),
    )

    registrations_details = models.TextField(
        _("Namelijk"),
        max_length=1500,
        blank=True,
    )

    registration_kinds = models.ManyToManyField(
        RegistrationKind,
        verbose_name=_("Kies het soort meting"),
        blank=True,
    )

    registration_kinds_details = models.TextField(
        _("Namelijk"),
        max_length=1500,
        blank=True,
    )

    # Fields with respect to experimental design
    has_intervention = models.BooleanField(_("Interventieonderzoek"), default=False)
    has_observation = models.BooleanField(_("Observatieonderzoek"), default=False)
    has_sessions = models.BooleanField(
        _("Taakonderzoek en/of interview(s)"), default=False
    )

    # Fields with respect to Sessions
    deception = models.CharField(
        _(
            "Is er binnen bovenstaand onderzoekstraject sprake van "
            "misleiding van de deelnemer?"
        ),
        help_text=_(
            "Misleiding is het doelbewust verschaffen van inaccurate "
            "informatie over het doel en/of belangrijke aspecten van de gang van zaken "
            'tijdens het onderzoek. Denk aan zaken als een bewust misleidende "cover story" '
            "voor het experiment; het ten onrechte suggereren dat er door de deelnemer met andere "
            "deelnemers wordt samengewerkt; het onaangekondigd aanbieden van een cruciale "
            "geheugentaak of het geven van gefingeerde feedback. Wellicht ten overvloede: "
            "het gaat hierbij niet om fillers in bijv. taalwetenschappelijk onderzoek."
        ),
        max_length=1,
        choices=YesNoDoubt.choices,
        blank=True,
    )
    deception_details = models.TextField(
        _(
            "Geef een toelichting en beschrijf hoe en wanneer de deelnemer "
            "zal worden gedebrieft."
        ),
        blank=True,
    )
    negativity = models.CharField(
        _(
            "Bevat bovenstaand onderzoekstraject elementen die <em>tijdens"
            "</em> de deelname zodanig belastend zijn dat deze vragen, "
            "weerstand, of zelfs verontwaardiging zouden kunnen oproepen, "
            "bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, "
            "of bij ouders of andere vertegenwoordigers?"
        ),
        max_length=1,
        choices=YesNoDoubt.choices,
        blank=True,
    )
    negativity_details = models.TextField(
        _("Licht toe"),
        max_length=1000,
        help_text=_(
            "Geef concrete voorbeelden van de relevante aspecten van jouw "
            "onderzoek (bijv. voorbeelden van mogelijk zeer kwetsende woorden "
            "of uitspraken in de taak; zeer confronterende vragen in een "
            "vragenlijst; negatieve feedback), zodat de commissie zich een "
            "goed beeld kan vormen."
        ),
        blank=True,
    )

    risk = models.CharField(
        _(
            "Zijn er kwesties rondom de veiligheid van, of risico's voor de "
            "deelnemers <em>tijdens of na</em> deelname aan het onderzoek?"
        ),
        help_text=mark_safe_lazy(
            _(
                "Houd hierbij niet alleen rekening met mogelijke psychische "
                "of fysieke schadelijke gevolgen, maar ook met andere "
                "mogelijke schade, zoals bijv. stigmatisering, "
                "(re-)traumatisering, aantasting van zelfbeeld, verlies van "
                "privacy, toevalsbevindingen, juridische vervolging of "
                "aansprakelijkheid, e.d."
            )
        ),
        max_length=1,
        choices=YesNoDoubt.choices,
        blank=True,
    )
    risk_details = models.TextField(_("Licht toe"), max_length=1000, blank=True)

    # References
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)

    class Meta:
        ordering = ["order"]
        unique_together = ("proposal", "order")

    def get_intervention(self):
        if self.has_intervention and hasattr(self, "intervention"):
            return self.intervention

    def get_observation(self):
        if self.has_observation and hasattr(self, "observation"):
            return self.observation

    def get_sessions(self):
        if self.has_sessions:
            return self.session_set.all()
        return []

    @property
    def sessions_number(self):
        return self.session_set.count()

    def first_session(self):
        """Returns the first Session in this Study"""
        return self.session_set.order_by("order")[0]

    def last_session(self):
        """Returns the last Session in this Study"""
        return self.session_set.order_by("-order")[0]

    def has_children(self):
        """Returns whether the Study contains non-adult AgeGroups"""
        return self.age_groups.filter(is_adult=False).exists()

    def has_adults(self):
        """Returns whether the Study contains adult AgeGroups"""
        return self.age_groups.filter(is_adult=True).exists()

    def has_participants_below_age(self, age):
        """Returns whether the Study contains AgeGroups with ages below the specified age"""
        return self.age_groups.filter(Q(age_min__lt=age) & Q(age_max__lt=age)).exists()

    def design_started(self):
        """Checks if the design phase has started"""
        return any([self.has_intervention, self.has_observation, self.has_sessions])

    def design_completed(self):
        """Checks if the design phase has been completed"""
        result = self.design_started()
        if self.has_intervention:
            result &= hasattr(self, "intervention")
        if self.has_observation:
            result &= hasattr(self, "observation")
        if self.has_sessions:
            if self.session_set.all():
                result &= self.last_session().tasks_duration is not None
            else:
                result = False
        return result

    def is_completed(self):
        """Checks if the whole Study has been completed"""
        return self.design_completed() and self.risk != ""

    def has_missing_forms(self):
        documents = self.get_documents_object()
        return not documents.informed_consent or not documents.briefing

    def has_missing_sessions(self):
        if self.get_intervention() and self.intervention.extra_task:
            return (
                self.intervention.settings_contains_schools() and not self.has_sessions
            )

        return False

    def has_no_sessions(self):
        return self.has_sessions and self.sessions_number == 0

    def has_recordings(
        self,
    ):
        if self.registrations.filter(is_recording=True):
            return True
        return False

    def research_settings_contains_schools(self):
        """
        Checks if any research track contains a school in its setting.
        """
        if self.get_intervention() and self.intervention.settings_contains_schools():
            return True

        if (
            self.get_sessions()
            and self.session_set.filter(setting__is_school=True).exists()
        ):
            return True

        if self.get_observation() and self.observation.settings_contains_schools():
            return True

        return False

    def get_gatekeeper_desiredness(self):
        """
        Return the highest gatekeeper document desiredness of this study, or
        False if undesired.
        """
        from main.models import GatekeeperChoices
        from attachments.utils import desiredness

        setting_models = list(self.get_sessions())
        setting_models += [sm for sm in [self.get_intervention()] if sm]
        setting_models += [sm for sm in [self.get_observation()] if sm]
        result = False
        for sm in setting_models:
            requirement = sm.gatekeeper_requirement
            if requirement is GatekeeperChoices.REQUIRED:
                return desiredness.REQUIRED
            if requirement is GatekeeperChoices.OPTIONAL:
                result = desiredness.OPTIONAL
        return result

    def needs_additional_external_forms(self):
        """This method checks if the school/other external institution forms
        are needed"""

        return self.research_settings_contains_schools()

    def get_documents_object(self):
        """Gets the document object for this study"""
        # The self.proposal should be a bit redundant, but semantically nice
        return Documents.objects.get(study=self, proposal=self.proposal)

    def __str__(self):
        return _("Study details for proposal %s") % self.proposal.title

    # DEFUNCT: Passive consent has been removed from studies.
    # These fields are kept for posterity as to not break older proposals.
    passive_consent = models.BooleanField(
        _("Maak je gebruik van passieve toestemming?"),
        help_text=mark_safe_lazy(
            _(
                'Wanneer je kinderen via een instelling \
(dus ook school) werft en je de ouders niet laat ondertekenen, maar in \
plaats daarvan de leiding van die instelling, dan maak je gebruik van \
passieve toestemming. Je kan de templates vinden op \
<a href="https://intranet.uu.nl/documenten-ethische-toetsingscommissie-gw" \
target="_blank">de FETC-GW-website</a>.'
            )
        ),
        null=True,
        blank=True,
    )
    passive_consent_details = models.TextField(
        _(
            "Licht je antwoord toe. Wij willen je wijzen op het reglement, \
sectie 3.1 'd' en 'e'. Passive consent is slechts in enkele gevallen \
toegestaan en draagt niet de voorkeur van de commissie."
        ),
        blank=True,
    )


class Documents(models.Model):
    """
    A model to store consent forms for a study and/or a proposal
    """

    study = models.OneToOneField(Study, on_delete=models.CASCADE, blank=True, null=True)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)

    informed_consent = models.FileField(
        _("Upload hier de toestemmingsverklaring (in .pdf of .doc(x)-formaat)"),
        help_text=_(
            "Als je de AVG grondslag 'Algemeen belang' gebruikt, en er helemaal geen toestemmingsverklaring nodig is (ook niet voor bijzondere persoonsgegevens of opnames), upload dan een leeg document in dit veld."
        ),
        blank=True,
        validators=[validate_pdf_or_doc],
        upload_to=INFORMED_CONSENT_FILENAME,
        storage=OverwriteStorage(),
    )

    briefing = models.FileField(
        _("Upload hier de informatiebrief (in .pdf of .doc(x)-formaat)"),
        blank=True,
        validators=[validate_pdf_or_doc],
        upload_to=BRIEFING_FILENAME,
        storage=OverwriteStorage(),
    )

    director_consent_declaration = models.FileField(
        _(
            "Upload hier de toestemmingsverklaring voor de leiding of het management van de instelling (in .pdf of .doc(x)-format)"
        ),
        blank=True,
        validators=[validate_pdf_or_doc],
        help_text=_(
            "Upload indien mogelijk een ondertekende versie van het document. Upload als deze nog niet bestaat een blanco versie, en stuur de ondertekende versie later op naar de secretaris van de FETC-GW."
        ),
        upload_to=DEPARTMENT_CONSENT_FILENAME,
        storage=OverwriteStorage(),
    )

    director_consent_information = models.FileField(
        _(
            "Upload hier de informatiebrief voor de leiding of het management van de instelling (in .pdf of .doc(x)-formaat)"
        ),
        blank=True,
        validators=[validate_pdf_or_doc],
        upload_to=DEPARTMENT_INFO_FILENAME,
        storage=OverwriteStorage(),
    )

    parents_information = models.FileField(
        _(
            "Upload hier de informatiebrief voor de ouders of verzorgers (in .pdf of .doc(x)-formaat)"
        ),
        blank=True,
        validators=[validate_pdf_or_doc],
        upload_to=PARENTAL_INFO_FILENAME,
        storage=OverwriteStorage(),
    )

    def save(self, *args, **kwargs):
        """
        To be a bit cleaner we do not save if this object is new, not connected to a study and if the document fields are
        empty.

        The edit consent form page contains 2 extra forms, but those are optional. However, Django creates instances
        for these forms anyway, so we have to

        """
        if (
            not self.study
            and not self.informed_consent
            and not self.briefing
            and not self.pk
        ):
            return

        super(Documents, self).save(*args, **kwargs)

    def __str__(self):
        if self.study:
            return "Documents object for study '{}', proposal '{}'".format(
                self.study, self.proposal
            )
        return "(Extra) Documents object for proposal '{}'".format(self.proposal)
