# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from django.utils.functional import lazy
from django.utils.safestring import mark_safe, SafeString

mark_safe_lazy = lazy(mark_safe, SafeString)

from main.models import YesNoDoubt
from main.validators import MaxWordsValidator, validate_pdf_or_doc
from .utils import available_urls, FilenameFactory, OverwriteStorage
from datetime import date, timedelta

logger = logging.getLogger(__name__)

SUMMARY_MAX_WORDS = 200
SELF_ASSESSMENT_MAX_WORDS = 1000
COMMENTS_MAX_WORDS = 1000
PROPOSAL_FILENAME = FilenameFactory("Proposal")
PREASSESSMENT_FILENAME = FilenameFactory("Preassessment")
DMP_FILENAME = FilenameFactory("DMP")
METC_DECISION_FILENAME = FilenameFactory("METC_Decision")
PRE_APPROVAL_FILENAME = FilenameFactory("Pre_Approval")


class Relation(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_supervisor = models.BooleanField(default=True)
    check_in_course = models.BooleanField(default=True)
    check_pre_assessment = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class StudentContext(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class Funding(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    needs_name = models.BooleanField(default=True)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class Institution(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    reviewing_chamber = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class ProposalQuerySet(models.QuerySet):
    DECISION_MADE = 55

    def archive_pre_filter(self):
        return self.filter(
            status__gte=self.DECISION_MADE,
            status_review=True,
            in_archive=True,
        )

    def no_embargo(self):
        return self.filter(
            models.Q(embargo_end_date__isnull=True)
            | models.Q(embargo_end_date__lt=date.today())
        )

    def public_archive(self):
        two_years_ago = date.today() - timedelta(weeks=104)
        return (
            self.archive_pre_filter()
            .no_embargo()
            .filter(
                date_confirmed__gt=two_years_ago,
            )
            .order_by("-date_reviewed")
        )

    def export(self):
        return self.archive_pre_filter().order_by("-date_reviewed")

    def users_only_archive(self, committee):
        return (
            self.archive_pre_filter()
            .no_embargo()
            .filter(
                is_pre_assessment=False,
                reviewing_committee=committee,
            )
            .select_related(
                # this optimizes the loading a bit
                "supervisor",
                "parent",
                "relation",
                "parent__supervisor",
                "parent__relation",
            )
            .prefetch_related(
                "applicants",
                "review_set",
                "parent__review_set",
                "study_set",
                "study_set__observation",
                "study_set__session_set",
                "study_set__intervention",
                "study_set__session_set__task_set",
            )
        )


class Proposal(models.Model):
    objects = ProposalQuerySet.as_manager()

    class Statuses(models.IntegerChoices):
        DRAFT = 1, _("Concept")
        SUBMITTED_TO_SUPERVISOR = 40, _(
            "Opgestuurd ter beoordeling door eindverantwoordelijke"
        )
        SUBMITTED = 50, _("Opgestuurd ter beoordeling door FETC-GW")
        DECISION_MADE = 55, _("Aanvraag is beoordeeld door FETC-GW")
        WMO_DECISION_MADE = 60, _("Aanvraag is beoordeeld door FETC-GW")

    class PracticeReasons(models.IntegerChoices):
        COURSE = 1, _("in het kader van een cursus")
        EXPLORATION = 2, _("om de portal te exploreren")

    # Fields of a proposal
    reference_number = models.CharField(
        max_length=20,
        unique=True,
    )

    reviewing_committee = models.ForeignKey(
        Group,
        verbose_name=_("Door welke comissie dient deze aanvraag te worden beoordeeld?"),
        help_text="",
        on_delete=models.PROTECT,
    )

    institution = models.ForeignKey(
        Institution,
        verbose_name=_("Aan welk onderzoeksinstituut ben je verbonden?"),
        on_delete=models.PROTECT,
    )

    date_start = models.DateField(
        _(
            "Wat is de beoogde startdatum van het onderzoek waarvoor deze aanvraag wordt ingediend?"
        ),
        help_text=_(
            "NB: Voor een aanvraag van een onderzoek dat al gestart is voordat \
de FETC-GW de aanvraag heeft goedgekeurd kan geen formele goedkeuring meer \
gegeven worden; de FETC-GW geeft in die gevallen een post-hoc advies."
        ),
        blank=True,
        null=True,
    )

    title = models.CharField(
        _(
            "Wat is de titel van je aanvraag? Deze titel zal worden gebruikt in "
            "alle formele correspondentie."
        ),
        max_length=200,
        unique=False,
        help_text=_(
            "De titel die je hier opgeeft is zichtbaar voor de \
FETC-GW-leden en, wanneer de aanvraag is goedgekeurd, ook voor alle \
medewerkers die in het archief van deze portal kijken. De titel mag niet \
identiek zijn aan een vorige titel van een aanvraag die je hebt ingediend."
        ),
    )

    summary = models.TextField(
        _(
            "Geef een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen. Gebruik maximaal 200 woorden."
        ),
        validators=[MaxWordsValidator(SUMMARY_MAX_WORDS)],
        blank=True,
    )

    other_applicants = models.BooleanField(
        _(
            "Zijn er nog andere onderzoekers bij deze aanvraag betrokken die geaffilieerd zijn aan één van de onderzoeksinstituten ICON, OFR, OGK of ILS?"
        ),
        default=None,
        null=True,
        help_text=mark_safe_lazy(
            _(
                "Werk je samen met een onderzoeker of "
                "organisatie buiten de UU en is je "
                "onderzoek niet strikt anoniem? Neem dan "
                "contact op met de <a "
                'href="mailto:privacy.gw@uu.nl">privacy '
                "officer</a>. "
                "Er moeten dan wellicht afspraken worden "
                "gemaakt over de verwerking van "
                "persoonsgegevens."
            )
        ),
    )

    other_stakeholders = models.BooleanField(
        mark_safe_lazy(
            _(
                "Zijn er nog andere onderzoekers bij deze aanvraag betrokken "
                "die <strong>niet</strong> geaffilieerd zijn aan een van de "
                "onderzoeksinstituten van de Faculteit Geestwetenschappen van de "
                "UU? Zoja, vermeld diens naam en affiliatie."
            )
        ),  # Note: form labels with HTML are hard-coded in form Meta classes
        default=None,
        null=True,
    )

    stakeholders = models.TextField(
        _("Naam en affiliatie van andere betrokkenen"),
        blank=True,
    )

    translated_forms = models.BooleanField(
        mark_safe_lazy(
            _(
                "Worden de documenten nog vertaald naar een andere taal dan Nederlands of Engels?"
            )
        ),
        default=None,
        blank=True,
        null=True,
    )

    translated_forms_languages = models.CharField(
        _("Andere talen:"),
        max_length=255,
        default=None,
        blank=True,
        null=True,
    )

    funding = models.ManyToManyField(
        Funding,
        verbose_name=_("Hoe wordt dit onderzoek gefinancierd?"),
        blank=True,
    )

    funding_details = models.CharField(
        _("Namelijk"),
        max_length=200,
        blank=True,
    )

    funding_name = models.CharField(
        _("Wat is de naam van het gefinancierde project en wat is het projectnummer?"),
        max_length=200,
        blank=True,
        help_text=_(
            "De titel die je hier opgeeft zal in de formele toestemmingsbrief "
            "gebruikt worden."
        ),
    )

    comments = models.TextField(
        _("Ruimte voor eventuele opmerkingen. Gebruik maximaal 1000 woorden."),
        validators=[MaxWordsValidator(COMMENTS_MAX_WORDS)],
        blank=True,
    )

    inform_local_staff = models.BooleanField(
        _(
            "<p>Je hebt aangegeven dat je gebruik wilt gaan maken van één \
van de faciliteiten van het ILS, namelijk de database, Zep software \
en/of het ILS lab. Het lab supportteam van het ILS zou graag op \
de hoogte willen worden gesteld van aankomende onderzoeken. \
Daarom vragen wij hier jouw toestemming om delen van deze aanvraag door te \
sturen naar het lab supportteam.</p> \
<p>Vind je het goed dat de volgende delen uit de aanvraag \
worden doorgestuurd:</p> \
- Jouw naam en de namen van de andere betrokkenen <br/> \
- De eindverantwoordelijke van het onderzoek <br/> \
- De titel van het onderzoek <br/> \
- De beoogde startdatum <br/> \
- Van welke faciliteiten je gebruik wil maken (database, lab, \
Zep software)"
        ),
        default=None,
        blank=True,
        null=True,
    )

    embargo = models.BooleanField(
        _(
            "Als de deelnemers van je onderzoek moeten worden misleid, kan \
          je ervoor kiezen je applicatie pas later op te laten nemen in het \
          publieke archief en het archief voor gebruikers \
          van dit portaal. Wil je dat jouw onderzoek tijdelijk onder \
          embargo wordt geplaatst?"
        ),
        default=None,
        blank=True,
        null=True,
    )

    embargo_end_date = models.DateField(
        _("Vanaf welke datum mag je onderzoek wel in het archief worden weergegeven?"),
        blank=True,
        null=True,
    )

    in_archive = models.BooleanField(default=False)

    is_pre_assessment = models.BooleanField(default=False)

    pre_assessment_pdf = models.FileField(
        _("Upload hier je aanvraag (in .pdf of .doc(x)-formaat)"),
        blank=True,
        upload_to=PREASSESSMENT_FILENAME,
        validators=[validate_pdf_or_doc],
    )

    is_pre_approved = models.BooleanField(
        _(
            "Heb je formele toestemming van een ethische toetsingcommissie, "
            "uitgezonderd deze FETC-GW commissie?"
        ),
        default=None,
        null=True,
        blank=True,
    )

    pre_approval_institute = models.CharField(
        _("Welk instituut heeft de aanvraag goedgekeurd?"),
        max_length=200,
        blank=True,
        null=True,
    )

    pre_approval_pdf = models.FileField(
        _(
            "Upload hier je formele toestemmingsbrief van dit instituut (in "
            ".pdf of .doc(x)-formaat)"
        ),
        blank=True,
        upload_to=PRE_APPROVAL_FILENAME,
        validators=[validate_pdf_or_doc],
    )

    in_course = models.BooleanField(
        _("Ik vul de portal in in het kader van een cursus"),
        default=False,
    )

    is_exploration = models.BooleanField(
        _("Ik vul de portal in om de portal te exploreren"),
        default=False,
    )

    pdf = models.FileField(
        blank=True,
        upload_to=PROPOSAL_FILENAME,
        storage=OverwriteStorage(),
    )

    # Fields with respect to Studies
    studies_similar = models.BooleanField(
        _(
            "Kan voor alle deelnemers dezelfde informatiebrief en, indien van \
          toepassing, dezelfde toestemmingsverklaring gebruikt worden?"
        ),
        help_text=_(
            "Daar waar de verschillen klein en qua belasting of \
risico irrelevant zijn is sprake van in essentie hetzelfde traject, en \
voldoet één set documenten voor de bijlagen. Denk \
hierbij aan taakonderzoek waarin de ene groep in taak X de ene helft van \
een set verhaaltjes te lezen krijgt, en de andere groep in taak X de andere \
helft. Of aan interventieonderzoek waarin drie vergelijkbare groepen op \
hetzelfde moment een verschillende interventie-variant krijgen (specificeer \
dan wel bij de beschrijving van de interventie welke varianten precies \
gebruikt worden). Let op: als verschillende groepen deelnemers verschillende \
<i>soorten</i> taken krijgen, dan kan dit niet en zijn dit afzonderlijke \
trajecten."
        ),
        blank=True,
        null=True,
    )

    studies_number = models.PositiveIntegerField(
        _("Hoeveel verschillende trajecten zijn er?"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    # Status
    status = models.PositiveIntegerField(
        choices=Statuses.choices,
        default=Statuses.DRAFT,
    )

    status_review = models.BooleanField(
        default=None,
        null=True,
        blank=True,
    )

    privacy_officer = models.BooleanField(
        _(
            "Ik heb mijn aanvraag en de documenten voor deelnemers besproken met de privacy officer."
        ),
        default=None,
        null=True,
        blank=True,
    )

    dmp_file = models.FileField(
        _(
            "Als je een Data Management Plan hebt voor deze aanvraag, "
            "kan je kiezen om deze hier bij te voegen. Het aanleveren van een "
            "DMP vergemakkelijkt het toetsingsproces aanzienlijk."
        ),
        blank=True,
        validators=[validate_pdf_or_doc],
        upload_to=DMP_FILENAME,
        storage=OverwriteStorage(),
    )

    # Confirmation
    confirmation_comments = models.TextField(
        _("Ruimte voor eventuele opmerkingen"),
        blank=True,
    )

    # Dates for bookkeeping
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_submitted_supervisor = models.DateTimeField(null=True)
    date_reviewed_supervisor = models.DateTimeField(null=True)
    date_submitted = models.DateTimeField(null=True)
    date_reviewed = models.DateTimeField(null=True)
    date_confirmed = models.DateField(
        _("Datum bevestigingsbrief verstuurd"),
        null=True,
    )

    has_minor_revision = models.BooleanField(
        _("Is er een revisie geweest na het indienen van deze aanvraag?"),
        default=False,
    )

    minor_revision_description = models.TextField(
        _("Leg uit"),
        null=True,
        blank=True,
    )

    self_assessment = models.TextField(
        _(
            "Wat zijn de belangrijkste ethische kwesties in dit onderzoek en "
            "beschrijf kort hoe ga je daarmee omgaat.  Gebruik maximaal 1000 "
            "woorden."
        ),
        blank=True,
        validators=[
            MaxWordsValidator(SELF_ASSESSMENT_MAX_WORDS),
        ],
    )
    knowledge_security = models.CharField(
        _("Zijn er kwesties rondom kennisveiligheid?"),
        help_text=mark_safe_lazy(
            _(
                "Kennisveiligheid gaat over het tijdig signaleren en mitigeren "
                "van veiligheidsrisico's bij wetenschappelijk onderzoek. Klik "
                "<a href='https://intranet.uu.nl/kennisbank/kennisveiligheid'>hier</a> "
                "voor meer informatie."
            )
        ),
        max_length=1,
        choices=YesNoDoubt.choices,
        blank=True,
    )
    knowledge_security_details = models.TextField(
        _("Licht toe"), max_length=200, blank=True
    )
    researcher_risk = models.CharField(
        _(
            "Zijn er kwesties rondom de veiligheid van of risico's voor de onderzoeker(s)?"
        ),
        help_text=_(
            "Houd hierbij niet alleen rekening met mogelijke psychische of "
            "fysieke schade, maar ook met andere mogelijke schade, zoals bijv. "
            "hiërarchische machtsverhoudingen in veldwerk, mogelijke negatieve "
            "gevolgen voor de zichtbaarheid/vindbaarheid van de onderzoeker in "
            "in het publieke domein, juridische vervolging of "
            "aansprakelijkheid, e.d."
        ),
        max_length=1,
        choices=YesNoDoubt.choices,
        blank=True,
    )
    researcher_risk_details = models.TextField(
        _("Licht toe"), max_length=200, blank=True
    )

    # References to other models
    relation = models.ForeignKey(
        Relation,
        verbose_name=_(
            "In welke hoedanigheid ben je betrokken \
bij dit onderzoek?"
        ),
        on_delete=models.CASCADE,
        blank=False,
        null=True,
    )

    student_program = models.CharField(
        verbose_name=_("Wat is je studierichting?"),
        max_length=200,
        blank=True,
    )

    student_context = models.ForeignKey(
        StudentContext,
        verbose_name=_("In welke context doe je dit onderzoek?"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    student_context_details = models.CharField(
        verbose_name=_("Namelijk:"),
        max_length=200,
        blank=True,
        null=True,
    )

    student_justification = models.TextField(
        verbose_name=_(
            "Studenten (die mensgebonden onderzoek uitvoeren binnen hun \
studieprogramma) hoeven in principe geen aanvraag in te dienen bij de \
FETC-GW. Bespreek met je begeleider of je daadwerkelijk een aanvraag \
moet indienen. Als dat niet hoeft kun je nu je aanvraag afbreken. \
Als dat wel moet, geef dan hier aan wat de reden is:"
        ),
        max_length=500,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_by",
        on_delete=models.CASCADE,
    )

    applicants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_(
            "Uitvoerenden, inclusief uzelf. Let op! De andere onderzoekers moeten \
        ten minste één keer zijn ingelogd op dit portaal om ze te kunnen selecteren."
        ),
        related_name="applicants",
    )

    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Promotor/Begeleider"),
        blank=True,
        null=True,
        help_text=_(
            """Je aanvraag moet, als je alles hebt ingevuld, via de portal 
                    naar je promotor of begeleider gestuurd worden. Deze persoon 
                    is de eindverantwoordelijk onderzoeker, en zal de aanvraag 
                    vervolgens waar nodig kunnen aanpassen en indienen bij de FETC-GW.
                    <br><br><strong>Belangrijk</strong>: als je je promotor of 
                    begeleider niet kunt vinden met dit veld, dan moeten zij 
                    waarschijnlijk eerst één keer inloggen in deze portal. 
                    Je kunt nog wel verder met de aanvraag, maar vergeet dit veld 
                    niet in te vullen voor je de aanvraag indient. Je aanvraag 
                    zal dan namelijk niet in behandeling kunnen worden genomen."""
        ),
        on_delete=models.CASCADE,
    )

    # Copying an existing Proposal
    parent = models.ForeignKey(
        "self",
        null=True,
        related_name="children",
        verbose_name=_("Te kopiëren aanvraag"),
        help_text=_(
            "Dit veld toont enkel aanvragen waar je zelf een medeuitvoerende " "bent."
        ),
        on_delete=models.CASCADE,
    )

    is_revision = models.BooleanField(
        _("Is deze aanvraag een revisie van of amendement op een ingediende aanvraag?"),
        default=False,
    )

    @property
    def is_revisable(self):
        """A check to see if a proposal is revisable. For use in Querysets,
        keep in mind to also check if the user is one of the applicants
        or the supervisor."""
        if (
            not self.is_pre_assessment
            and not self.status_review
            and self.status == self.Statuses.DECISION_MADE
            and not self.children.all()
        ):
            return True
        return False

    def is_practice(self):
        return self.in_course or self.is_exploration

    def accountable_user(self):
        return self.supervisor if self.relation.needs_supervisor else self.created_by

    @property
    def stepper(self,):
        if not getattr(self, "_stepper", None):
            # Importing here to avoid circular import
            from proposals.utils.stepper import Stepper
            self._stepper = Stepper(self)
        return self._stepper

    def continue_url(self):
        stepper = self.stepper
        for item in stepper.items:
            if item.get_errors():
                return item.get_url()
        return reverse("proposals:submit", args=[self.pk])

    def committee_prefixed_refnum(self):
        """Returns the reference number including the reviewing committee"""
        parts = (self.reviewing_committee.name, self.reference_number)
        return "-".join(parts)

    def available_urls(self):
        """Returns the available URLs for this Proposal"""
        return available_urls(self)

    def first_study(self):
        """Returns the first Study in this Proposal, or None if there's none."""
        return self.study_set.order_by("order")[0] if self.study_set.count() else None

    def last_study(self):
        """Returns the last Study in this Proposal, or None if there's none."""
        return self.study_set.order_by("-order")[0] if self.study_set.count() else None

    def current_study(self):
        """
        Returns the current (incomplete) Study.
        - If all Studies are completed, the last Study is returned.
        - If no Studies have yet been created, None is returned.
        """
        current_study = None
        for study in self.study_set.all():
            current_study = study
            if not study.is_completed():
                break
        return current_study

    def current_session(self):
        """
        Returns the current (incomplete) Session.
        - If all Sessions are completed, the last Session is returned.
        - If no Sessions have yet been created, None is returned.
        """
        current_session = None
        for study in self.study_set.all().prefetch_related("session_set"):
            for session in study.session_set.all():
                current_session = session
                if session.tasks_duration is None:
                    break
        return current_session

    def amendment_or_revision(self):
        if self.is_revision and self.parent:
            return _("Amendement") if self.parent.status_review else _("Revisie")

    def type(self):
        """
        Returns the type of a Study: either normal, revision, amendment, preliminary assessment or practice
        """
        result = _("Normaal")
        amendment_or_revision = self.amendment_or_revision()
        if amendment_or_revision is not None:
            result = amendment_or_revision
        elif self.is_pre_assessment:
            result = _("Voortoetsing")
        elif self.is_practice():
            result = _("Oefening")
        elif self.is_pre_approved:
            result = _("Extern getoetst")

        return result

    def supervisor_decision(self):
        """Returns the Decision of the supervisor for this Proposal (if any and in current stage)"""
        from reviews.models import Review, Decision

        if self.supervisor and self.status == Proposal.Statuses.SUBMITTED_TO_SUPERVISOR:
            decisions = Decision.objects.filter(
                review__proposal=self, review__stage=Review.Stages.SUPERVISOR
            ).order_by("-pk")

            if decisions:
                return decisions[0]

            from reviews.utils import start_supervisor_phase

            start_supervisor_phase(self)

            return self.supervisor_decision()

    def latest_review(self):
        from reviews.models import Review

        return Review.objects.filter(proposal=self).last()

    def enforce_wmo(self):
        """Send proposal back to draft phase with WMO enforced."""
        self.status = self.Statuses.DRAFT
        self.save()
        self.wmo.enforced_by_commission = True
        self.wmo.save()

    def mark_reviewed(self, continuation, time=None):
        """Finalize a proposal after a decision has been made."""
        if time is None:
            time = timezone.now()
        self.status = self.Statuses.DECISION_MADE
        # Importing here to prevent circular import
        from reviews.models import Review

        self.status_review = continuation in [
            Review.Continuations.GO,
            Review.Continuations.GO_POST_HOC,
        ]
        self.date_reviewed = time
        self.generate_pdf()
        self.save()

    def generate_pdf(self, force_overwrite=False):
        """Generate _and save_ a pdf of the proposal for posterity.
        The currently existing PDF will not be overwritten unless the
        force_overwrite keyword is True."""
        from proposals.utils import generate_pdf

        pdf = generate_pdf(self)
        if force_overwrite is True or not self.use_canonical_pdf or not self.pdf:
            self.pdf.save(
                PROPOSAL_FILENAME(self, "document.pdf"),
                pdf,
            )
            self.save()
        else:
            logger.warn(
                f"Not saving PDF of {self.reference_number} "
                "to preserve canonical PDF.",
            )
        return pdf

    def use_canonical_pdf(self):
        """Returns False if this proposal should regenerate its PDF
        on request. Proposals that have already been decided on should
        rely on a PDF generated at time of review, so that the PDF
        generation templates can evolve without breaking older proposals."""
        return self.status_review is not None

    def __str__(self):
        if self.is_practice():
            return "{} ({}) (Practice)".format(self.title, self.created_by)
        return "{} ({})".format(self.title, self.created_by)


class Wmo(models.Model):
    class WMOStatuses(models.IntegerChoices):
        NO_WMO = 0, _("Geen beoordeling door METC noodzakelijk")
        WAITING = 1, _("In afwachting beslissing METC")
        JUDGED = 2, _("Beslissing METC geüpload")

    metc = models.CharField(
        _(
            "Vindt de dataverzameling plaats binnen het UMC Utrecht of \
andere instelling waar toetsing door een METC verplicht is gesteld?"
        ),
        max_length=1,
        choices=YesNoDoubt.choices,
        blank=True,
        default=None,
    )

    metc_details = models.TextField(
        _("Licht toe"),
        blank=True,
    )

    metc_institution = models.CharField(
        _("Welke instelling?"),
        max_length=200,
        blank=True,
    )

    is_medical = models.CharField(
        _(
            "Is de onderzoeksvraag medisch-wetenschappelijk van aard \
(zoals gedefinieerd door de WMO)?"
        ),
        help_text=_(
            "De definitie van medisch-wetenschappelijk onderzoek is: \
Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het \
beantwoorden van een vraag op het gebied van ziekte en gezondheid \
(etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, \
uitkomst of behandeling van ziekte), door het op systematische wijze \
vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen \
aan medische kennis die ook geldend is voor populaties buiten de directe \
onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk \
onderzoek, 2005, ccmo.nl)"
        ),
        max_length=1,
        choices=YesNoDoubt.choices,
        blank=True,
    )

    metc_application = models.BooleanField(
        _(
            "Je onderzoek moet beoordeeld worden door een METC, maar dient nog \
wel bij de FETC-GW te worden geregistreerd. Is dit onderzoek al aangemeld \
bij een METC?"
        ),
        default=False,
    )

    metc_decision = models.BooleanField(
        _("Is de METC al tot een beslissing gekomen?"),
        default=False,
    )

    metc_decision_pdf = models.FileField(
        _(
            "Upload hier de beslissing van het METC \
(in .pdf of .doc(x)-formaat)"
        ),
        blank=True,
        validators=[validate_pdf_or_doc],
        upload_to=METC_DECISION_FILENAME,
        storage=OverwriteStorage(),
    )

    # Status
    status = models.PositiveIntegerField(
        choices=WMOStatuses.choices,
        default=WMOStatuses.NO_WMO,
    )

    enforced_by_commission = models.BooleanField(default=False)

    # References
    proposal = models.OneToOneField(
        Proposal,
        primary_key=True,
        on_delete=models.CASCADE,
    )

    def save(self, *args, update_fields=None, **kwargs):
        """Sets the correct status on save of a WMO"""
        self.update_status()
        # If update_fields is supplied, we need to add status to it (or it will be ignored)
        if update_fields is not None and "name" in update_fields:
            update_fields = {"status"}.union(update_fields)
        super(Wmo, self).save(*args, update_fields=update_fields, **kwargs)

    def update_status(self):
        if (
            self.metc == YesNoDoubt.YES
            or self.is_medical == YesNoDoubt.YES
            or self.enforced_by_commission
        ):
            if self.metc_decision and self.metc_decision_pdf:
                self.status = self.WMOStatuses.JUDGED
            else:
                self.status = self.WMOStatuses.WAITING
        else:
            self.status = self.WMOStatuses.NO_WMO

    def __str__(self):
        return _("WMO {title}, status {status}").format(
            title=self.proposal.title, status=self.status
        )
