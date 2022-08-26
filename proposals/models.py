# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.utils.functional import lazy
from django.utils.safestring import mark_safe
mark_safe_lazy = lazy(mark_safe, str)

from main.models import YES, YES_NO_DOUBT
from main.validators import MaxWordsValidator, validate_pdf_or_doc
from .validators import AVGUnderstoodValidator
from .utils import available_urls, FilenameFactory, OverwriteStorage

SUMMARY_MAX_WORDS = 200
PROPOSAL_FILENAME = FilenameFactory('Proposal')
PREASSESSMENT_FILENAME = FilenameFactory('Preassessment')
DMP_FILENAME = FilenameFactory('DMP')
METC_DECISION_FILENAME = FilenameFactory('METC_Decision')
PRE_APPROVAL_FILENAME = FilenameFactory('Pre_Approval')


class Relation(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_supervisor = models.BooleanField(default=True)
    check_in_course = models.BooleanField(default=True)
    check_pre_assessment = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.description


class Funding(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    needs_name = models.BooleanField(default=True)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

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
        ordering = ['order']

    def __str__(self):
        return self.description


class Proposal(models.Model):
    DRAFT = 1
    SUBMITTED_TO_SUPERVISOR = 40
    SUBMITTED = 50
    DECISION_MADE = 55
    WMO_DECISION_MADE = 60
    STATUSES = (
        (DRAFT, _('Concept')),

        (SUBMITTED_TO_SUPERVISOR,
         _('Opgestuurd ter beoordeling door eindverantwoordelijke')),
        (SUBMITTED, _('Opgestuurd ter beoordeling door FETC-GW')),

        (DECISION_MADE, _('Aanvraag is beoordeeld door FETC-GW')),
        (WMO_DECISION_MADE, _('Aanvraag is beoordeeld door FETC-GW')),
    )

    COURSE = 1
    EXPLORATION = 2
    PRACTICE_REASONS = (
        (COURSE, _('in het kader van een cursus')),
        (EXPLORATION, _('om de portal te exploreren')),
    )

    # Fields of a proposal
    reference_number = models.CharField(
        max_length=20,
        unique=True,
    )

    reviewing_committee = models.ForeignKey(
        Group,
        verbose_name=_(
            'Door welke comissie dient deze aanvraag te worden beoordeeld?'
        ),
        help_text="",
        on_delete=models.PROTECT,
    )

    institution = models.ForeignKey(
        Institution,
        verbose_name=_(
            'Aan welk onderzoeksinstituut ben je verbonden?'
        ),
        on_delete=models.PROTECT,
    )

    date_start = models.DateField(
        _('Wat is de beoogde startdatum van het onderzoek waarvoor deze aanvraag wordt ingediend?'),
        blank=True,
        null=True,
    )

    title = models.CharField(
        _(
            'Wat is de titel van je aanvraag? Deze titel zal worden gebruikt in '
            'alle formele correspondentie.'
        ),
        max_length=200,
        unique=False,
        help_text=_('De titel die je hier opgeeft is zichtbaar voor de \
FETC-GW-leden en, wanneer de aanvraag is goedgekeurd, ook voor alle \
medewerkers die in het archief van deze portal kijken. De titel mag niet \
identiek zijn aan een vorige titel van een aanvraag die je hebt ingediend.'),
    )

    summary = models.TextField(
        _(
            'Geef een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen. Gebruik maximaal 200 woorden.'
        ),
        validators=[MaxWordsValidator(SUMMARY_MAX_WORDS)],
        blank=True,
    )

    other_applicants = models.BooleanField(
        _(
            'Zijn er nog andere onderzoekers bij deze aanvraag betrokken die geaffilieerd zijn aan één van de onderzoeksinstituten ICON, OFR, OGK of UiL OTS?'
        ),
        default=False,
    )

    other_stakeholders = models.BooleanField(
        mark_safe_lazy(_('Zijn er nog andere onderzoekers bij deze aanvraag betrokken '
          'die <strong>niet</strong> geaffilieerd zijn aan een van de '
          'onderzoeksinstituten van de Faculteit Geestwetenschappen van de '
          'UU? ')), # Note: form labels with HTML are hard-coded in form Meta classes
        default=False,
    )

    stakeholders = models.TextField(
        _('Andere betrokkenen'),
        blank=True,
    )

    funding = models.ManyToManyField(
        Funding,
        verbose_name=_('Hoe wordt dit onderzoek gefinancierd?'),
        blank=True,
    )

    funding_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True,
    )

    funding_name = models.CharField(
        _('Wat is de naam van het gefinancierde project?'),
        max_length=200,
        blank=True,
        help_text=_(
            'De titel die je hier opgeeft zal in de formele toestemmingsbrief '
            'gebruikt worden.'
        ),
    )

    comments = models.TextField(
        _('Ruimte voor eventuele opmerkingen'),
        blank=True,
    )

    inform_local_staff = models.BooleanField(
        _('<p>Je hebt aangegeven dat je gebruik wilt gaan maken van één \
van de faciliteiten van het UiL OTS, namelijk de database, Zep software \
en/of het UiL OTS lab. Het lab supportteam van het UiL OTS zou graag op \
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
Zep software)'),
        default=None,
        blank=True,
        null=True
    )

    in_archive = models.BooleanField(default=False)

    public = models.BooleanField(default=True)

    is_pre_assessment = models.BooleanField(default=False)

    pre_assessment_pdf = models.FileField(
        _('Upload hier je aanvraag (in .pdf of .doc(x)-formaat)'),
        blank=True,
        upload_to=PREASSESSMENT_FILENAME,
        validators=[validate_pdf_or_doc],
    )

    is_pre_approved = models.BooleanField(
        _(
            'Heb je formele toestemming van een ethische toetsingcommissie, '
            'uitgezonderd deze FETC-GW commissie?'),
        default=None,
        null=True,
        blank=True,
    )

    pre_approval_institute = models.CharField(
        _('Welk instituut heeft de aanvraag goedgekeurd?'),
        max_length=200,
        blank=True,
        null=True,
    )

    pre_approval_pdf = models.FileField(
        _(
            'Upload hier je formele toestemmingsbrief van dit instituut (in '
            '.pdf of .doc(x)-formaat)'),
        blank=True,
        upload_to=PRE_APPROVAL_FILENAME,
        validators=[validate_pdf_or_doc],
    )

    in_course = models.BooleanField(
        _('Ik vul de portal in in het kader van een cursus'),
        default=False,
    )

    is_exploration = models.BooleanField(
        _('Ik vul de portal in om de portal te exploreren'),
        default=False,
    )

    pdf = models.FileField(
        blank = True,
        upload_to=PROPOSAL_FILENAME,
        storage=OverwriteStorage(),
    )

    # Fields with respect to Studies
    studies_similar = models.BooleanField(
        _('Kan voor alle deelnemersgroepen dezelfde informatiebrief en \
        toestemmingsverklaring gebruikt worden?'),
        help_text=_('Daar waar de verschillen klein en qua belasting of \
risico irrelevant zijn is sprake van in essentie hetzelfde traject, en \
voldoet één set documenten voor de informed consent. Denk \
hierbij aan taakonderzoek waarin de ene groep in taak X de ene helft van \
een set verhaaltjes te lezen krijgt, en de andere groep in taak X de andere \
helft. Of aan interventieonderzoek waarin drie vergelijkbare groepen op \
hetzelfde moment een verschillende interventie-variant krijgen (specificeer \
dan wel bij de beschrijving van de interventie welke varianten precies \
gebruikt worden). Let op: als verschillende groepen deelnemers verschillende \
<i>soorten</i> taken krijgen, dan kan dit niet en zijn dit afzonderlijke \
trajecten.'),
        blank=True,
        null=True,
    )

    studies_number = models.PositiveIntegerField(
        _('Hoeveel verschillende trajecten zijn er?'),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    # Status
    status = models.PositiveIntegerField(
        choices=STATUSES,
        default=DRAFT,
    )

    status_review = models.BooleanField(
        default=None,
        null=True,
        blank=True,
    )

    avg_understood = models.BooleanField(
        _('Ik heb kennis genomen van het bovenstaande en begrijp mijn verantwoordelijkheden ten opzichte van de AVG.'),
        default=False,
        null=False,
        validators=[AVGUnderstoodValidator],
    )

    dmp_file = models.FileField(
        _('Als je een Data Management Plan hebt voor deze aanvraag, '
          'kan je kiezen om deze hier bij te voegen. Het aanleveren van een '
          'DMP vergemakkelijkt het toetsingsproces aanzienlijk.'),
        blank=True,
        validators=[validate_pdf_or_doc],
        upload_to=DMP_FILENAME,
        storage=OverwriteStorage(),
    )


    # Confirmation
    confirmation_comments = models.TextField(
        _('Ruimte voor eventuele opmerkingen'),
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
        _('Datum bevestigingsbrief verstuurd'),
        null=True,
    )

    has_minor_revision = models.BooleanField(
        _('Is er een revisie geweest na het indienen van deze aanvraag?'),
        default=False,
    )

    minor_revision_description = models.TextField(
        _('Leg uit'),
        null=True,
        blank=True,
    )

    self_assessment = models.TextField(
        _('Wat zijn de belangrijkste ethische kwesties in dit onderzoek en beschrijf kort hoe ga je daarmee omgaat.'),
        max_length=500,
        blank=True,
    )

    # References to other models
    relation = models.ForeignKey(
        Relation,
        verbose_name=_('In welke hoedanigheid ben je betrokken \
bij dit onderzoek?'),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    student_program = models.CharField(
        verbose_name=_('Wat is je studierichting?'),
        max_length = 200,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_by',
        on_delete=models.CASCADE,
    )

    applicants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Uitvoerende(n) (inclusief uzelf)'),
        related_name='applicants',
    )

    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Eindverantwoordelijke onderzoeker'),
        blank=True,
        null=True,
        help_text=_('''Aan het einde van de procedure kan je deze aanvraag ter
        verificatie naar je eindverantwoordelijke sturen. De
        eindverantwoordelijke zal de aanvraag vervolgens kunnen aanpassen en
        indienen bij de FETC-GW. <br><br><strong>NB</strong>: als je je
        eindverantwoordelijke niet kunt vinden met dit veld, moeten zij
        waarschijnlijk eerst één keer inloggen in deze portal. Je kunt nog wel
        verder met de aanvraag, maar vergeet dit veld niet in te vullen voor je de
        aanvraag indient.'''),
        on_delete=models.CASCADE,
    )

    # Copying an existing Proposal
    parent = models.ForeignKey(
        'self',
        null=True,
        related_name='children',
        verbose_name=_('Te kopiëren aanvraag'),
        help_text=_(
            'Dit veld toont enkel aanvragen waar je zelf een medeuitvoerende '
            'bent.'),
        on_delete=models.CASCADE,
    )

    is_revision = models.BooleanField(
        _(
            'Is deze aanvraag een revisie van of amendement op een ingediende aanvraag?'
        ),
        default=False,
    )

    def is_practice(self):
        return self.in_course or self.is_exploration

    def accountable_user(self):
        return self.supervisor if self.relation.needs_supervisor else self.created_by

    def continue_url(self):
        """Returns the next URL for this Proposal"""
        available_urls = self.available_urls()
        # For copies, always start at the first available URL
        if self.parent:
            result = available_urls[0].url
        # Otherwise, loop through the available URLs to find the last non-title with an URL
        else:
            for available_url in available_urls:
                if available_url.url and not available_url.is_title:
                    result = available_url.url
        return result

    def committee_prefixed_refnum(self):
        """Returns the reference number including the reviewing committee"""
        parts = (self.reviewing_committee.name, self.reference_number)
        return '-'.join(parts)

    def available_urls(self):
        """Returns the available URLs for this Proposal"""
        return available_urls(self)

    def first_study(self):
        """Returns the first Study in this Proposal, or None if there's none."""
        return self.study_set.order_by('order')[
            0] if self.study_set.count() else None

    def last_study(self):
        """Returns the last Study in this Proposal, or None if there's none."""
        return self.study_set.order_by('-order')[
            0] if self.study_set.count() else None

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
        for study in self.study_set.all().prefetch_related('session_set'):
            for session in study.session_set.all():
                current_session = session
                if session.tasks_duration is None:
                    break
        return current_session

    def type(self):
        """
        Returns the type of a Study: either normal, revision, amendment, preliminary assessment or practice
        """
        result = _('Normaal')
        if self.is_revision and self.parent:
            if self.parent.status_review:
                result = _('Amendement')
            else:
                result = _('Revisie')
        elif self.is_pre_assessment:
            result = _('Voortoetsing')
        elif self.is_practice():
            result = _('Oefening')
        elif self.is_pre_approved:
            result = _('Extern getoetst')

        return result

    def supervisor_decision(self):
        """Returns the Decision of the supervisor for this Proposal (if any and in current stage)"""
        from reviews.models import Review, Decision

        if self.supervisor and self.status == Proposal.SUBMITTED_TO_SUPERVISOR:
            decisions = Decision.objects.filter(review__proposal=self,
                                                review__stage=Review.SUPERVISOR).order_by(
                '-pk')

            if decisions:
                return decisions[0]

            from reviews.utils import start_supervisor_phase
            start_supervisor_phase(self)

            return self.supervisor_decision()

    def latest_review(self):
        from reviews.models import Review

        return Review.objects.filter(proposal=self).last()

    def __str__(self):
        if self.is_practice():
            return '{} ({}) (Practice)'.format(self.title, self.created_by)
        return '{} ({})'.format(self.title, self.created_by)


class Wmo(models.Model):
    NO_WMO = 0
    WAITING = 1
    JUDGED = 2
    WMO_STATUSES = (
        (NO_WMO, _('Geen beoordeling door METC noodzakelijk')),
        (WAITING, _('In afwachting beslissing METC')),
        (JUDGED, _('Beslissing METC geüpload')),
    )

    metc = models.CharField(
        _('Vindt de dataverzameling plaats binnen het UMC Utrecht of \
andere instelling waar toetsing door een METC verplicht is gesteld?'),
        max_length=1,
        choices=YES_NO_DOUBT,
        blank=True,
        default=None,
    )

    metc_details = models.TextField(
        _('Licht toe'),
        blank=True,
    )

    metc_institution = models.CharField(
        _('Welke instelling?'),
        max_length=200,
        blank=True,
    )

    is_medical = models.CharField(
        _('Is de onderzoeksvraag medisch-wetenschappelijk van aard \
(zoals gedefinieerd door de WMO)?'),
        help_text=_('De definitie van medisch-wetenschappelijk onderzoek is: \
Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het \
beantwoorden van een vraag op het gebied van ziekte en gezondheid \
(etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, \
uitkomst of behandeling van ziekte), door het op systematische wijze \
vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen \
aan medische kennis die ook geldend is voor populaties buiten de directe \
onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk \
onderzoek, 2005, ccmo.nl)'),
        max_length=1,
        choices=YES_NO_DOUBT,
        blank=True,
    )


    metc_application = models.BooleanField(
        _('Je onderzoek moet beoordeeld worden door een METC, maar dient nog \
wel bij de FETC-GW te worden geregistreerd. Is dit onderzoek al aangemeld \
bij een METC?'),
        default=False,
    )

    metc_decision = models.BooleanField(
        _('Is de METC al tot een beslissing gekomen?'),
        default=False,
    )

    metc_decision_pdf = models.FileField(
        _('Upload hier de beslissing van het METC \
(in .pdf of .doc(x)-formaat)'),
        blank=True,
        validators=[validate_pdf_or_doc],
        upload_to=METC_DECISION_FILENAME,
        storage=OverwriteStorage(),
    )

    # Status
    status = models.PositiveIntegerField(
        choices=WMO_STATUSES,
        default=NO_WMO,
    )

    enforced_by_commission = models.BooleanField(default=False)

    # References
    proposal = models.OneToOneField(
        Proposal,
        primary_key=True,
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a WMO"""
        self.update_status()
        super(Wmo, self).save(*args, **kwargs)

    def update_status(self):
        if self.metc == YES or self.is_medical == YES or self.enforced_by_commission:
            if self.metc_decision and self.metc_decision_pdf:
                self.status = self.JUDGED
            else:
                self.status = self.WAITING
        else:
            self.status = self.NO_WMO

    def __str__(self):
        return _('WMO {title}, status {status}').format(
            title=self.proposal.title, status=self.status)
