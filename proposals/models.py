# -*- encoding: utf-8 -*-

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import YES_NO_DOUBT, YES
from core.validators import MaxWordsValidator, validate_pdf_or_doc


SUMMARY_MAX_WORDS = 200


class Relation(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_supervisor = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.description


class Funding(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.description


class Proposal(models.Model):
    DRAFT = 1
    SUBMITTED_TO_SUPERVISOR = 40
    SUBMITTED = 50
    DECISION_MADE = 55
    WMO_DECISION_MADE = 60
    STATUSES = (
        (DRAFT, _('Concept')),

        (SUBMITTED_TO_SUPERVISOR, _('Opgestuurd ter beoordeling door eindverantwoordelijke')),
        (SUBMITTED, _('Opgestuurd ter beoordeling door ETCL')),

        (DECISION_MADE, _('Studie is beoordeeld door ETCL')),
        (WMO_DECISION_MADE, _('Studie is beoordeeld door METC')),
    )

    # Fields of a proposal
    reference_number = models.CharField(
        max_length=16,
        unique=True)
    date_start = models.DateField(
        _('Wat is, indien bekend, de beoogde startdatum van uw studie?'),
        blank=True,
        null=True)
    title = models.CharField(
        _('Wat is de titel van uw studie?'),
        max_length=200,
        unique=True,
        help_text=_('Kies s.v.p. een titel die niet volledig identiek is aan die van eerder ingediende studies.'))
    summary = models.TextField(
        _('Geef een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen. Gebruik maximaal 200 woorden.'),
        validators=[MaxWordsValidator(SUMMARY_MAX_WORDS)])
    other_applicants = models.BooleanField(
        _('Zijn er nog andere UiL OTS-onderzoekers of -studenten bij deze studie betrokken?'),
        default=False)
    other_stakeholders = models.BooleanField(
        _('Zijn er onderzoekers van buiten UiL OTS bij deze studie betrokken?'),
        default=False)
    stakeholders = models.TextField(
        _('Andere betrokkenen'),
        blank=True)
    funding = models.ManyToManyField(
        Funding,
        verbose_name=_('Hoe wordt dit onderzoek gefinancierd?'))
    funding_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True)
    comments = models.TextField(
        _('Ruimte voor eventuele opmerkingen'),
        blank=True)

    # Fields with respect to Studies
    studies_similar = models.NullBooleanField(
        _('Doorlopen alle deelnemersgroepen in essentie hetzelfde traject?'),
        help_text=_(u'Daar waar de verschillen klein en qua belasting of \
risico irrelevant zijn is sprake van in essentie hetzelfde traject. Denk \
hierbij aan taakonderzoek waarin de ene groep in taak X de ene helft van \
een set verhaaltjes te lezen krijgt, en de andere groep in taak X de andere \
helft. Of aan interventieonderzoek waarin drie vergelijkbare groepen op \
hetzelfde moment een verschillende interventie-variant krijgen (specificeer \
dan wel bij de beschrijving van de interventie welke varianten precies \
gebruikt worden).'))
    studies_number = models.PositiveIntegerField(
        _('Hoeveel verschillende trajecten zijn er?'),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Status
    status = models.PositiveIntegerField(choices=STATUSES, default=DRAFT)

    # Dates for bookkeeping
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_submitted_supervisor = models.DateTimeField(null=True)
    date_reviewed_supervisor = models.DateTimeField(null=True)
    date_submitted = models.DateTimeField(null=True)
    date_reviewed = models.DateTimeField(null=True)

    # References to other models
    relation = models.ForeignKey(
        Relation,
        verbose_name=_('In welke hoedanigheid bent u betrokken \
bij deze UiL OTS studie?'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_by')
    applicants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Uitvoerende(n) (inclusief uzelf)'),
        related_name='applicants',
        help_text=_('Als uw medeonderzoeker niet in de lijst voorkomt, \
vraag hem dan een keer in te loggen in het webportaal.'))
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Eindverantwoordelijke onderzoeker'),
        blank=True,
        null=True,
        help_text=_('Aan het einde van de procedure kunt u deze studie ter verificatie naar uw eindverantwoordelijke \
sturen. De eindverantwoordelijke zal de studie vervolgens kunnen aanpassen en indienen bij de ETCL.'))
    parent = models.ForeignKey(
        'self',
        null=True,
        verbose_name=_(u'Te kopiëren studie'),
        help_text=_('Dit veld toont enkel studies waar u zelf een medeuitvoerende bent.'))

    def continue_url(self):
        study = self.current_study()

        next_url = reverse('proposals:update', args=(self.pk,))

        if hasattr(self, 'wmo'):
            next_url = reverse('proposals:wmo_update', args=(self.wmo.pk,))

        if study:
            next_url = reverse('studies:update', args=(study.pk,))

            if study.compensation:
                next_url = reverse('studies:design', args=(study.pk,))

            if study.has_intervention:
                if hasattr(study, 'intervention'):
                    next_url = reverse('interventions:update', args=(study.intervention.pk,))
                else:
                    next_url = reverse('interventions:create', args=(study.pk,))

            if study.has_observation:
                if hasattr(study, 'observation'):
                    next_url = reverse('observations:update', args=(study.observation.pk,))
                else:
                    next_url = reverse('observations:create', args=(study.pk,))

            if study.has_sessions:
                session = self.current_session()
                if session:
                    next_url = reverse('tasks:start', args=(session.pk,))
                    # TODO: fix below
                    # next_url = reverse('tasks:update', args=(session.current_task().pk,))
                    # next_url = reverse('tasks:end', args=(session.pk,))
                    # next_url = reverse('studies:session_end', args=(study.pk,))

        return next_url

    def first_study(self):
        """Returns the first Study in this Proposal, or None if there's none."""
        return self.study_set.order_by('order')[0] if self.study_set.count() else None

    def last_study(self):
        """Returns the last Study in this Proposal, or None if there's none."""
        return self.study_set.order_by('-order')[0] if self.study_set.count() else None

    def current_study(self):
        """
        Returns the current (incomplete) Study.
        - If all Studies are completed, the last Study is returned.
        - If no Studies have yet been created, None is returned.
        """
        current_study = None
        for study in self.study_set.all():
            current_study = study
            if study.deception is None:
                break
        return current_study

    def current_session(self):
        """
        Returns the current (incomplete) Session.
        - If all Sessions are completed, the last Session is returned.
        - If no Sessions have yet been created, None is returned.
        """
        current_session = None
        for study in self.study_set.all():
            for session in study.session_set.all():
                current_session = session
                if session.tasks_duration is None:
                    break
        return current_session

    def __unicode__(self):
        return '%s (%s)' % (self.title, self.created_by)


class Wmo(models.Model):
    NO_WMO = 0
    WAITING = 1
    JUDGED = 2
    WMO_STATUSES = (
        (NO_WMO, _('Geen beoordeling door METC noodzakelijk')),
        (WAITING, _('In afwachting beslissing METC')),
        (JUDGED, _(u'Beslissing METC geüpload')),
    )

    metc = models.CharField(
        _('Vindt de dataverzameling plaats binnen het UMC Utrecht of \
andere instelling waar toetsing door een METC verplicht is gesteld?'),
        max_length=1,
        choices=YES_NO_DOUBT,
        blank=False,
        default=None)
    metc_details = models.TextField(
        _('Licht toe'),
        blank=True)
    metc_institution = models.CharField(
        _('Welke instelling?'),
        max_length=200,
        blank=True)
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
        blank=True)
    is_behavioristic = models.CharField(
        _('Worden de deelnemers aan een handeling onderworpen of worden \
hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?'),
        help_text=_('Een handeling of opgelegde gedragsregel varieert \
tussen het afnemen van weefsel bij een deelnemer tot de deelnemer een \
knop/toets in laten drukken.'),
        max_length=1,
        choices=YES_NO_DOUBT,
        blank=True)
    metc_application = models.BooleanField(
        _('Uw studie moet beoordeeld worden door de METC, maar dient nog \
wel bij de ETCL te worden geregistreerd. Is deze studie al aangemeld \
bij een METC?'),
        default=False)
    metc_decision = models.BooleanField(
        _('Is de METC al tot een beslissing gekomen?'),
        default=False)
    metc_decision_pdf = models.FileField(
        _('Upload hier de beslissing van het METC \
(in .pdf of .doc(x)-formaat)'),
        blank=True,
        validators=[validate_pdf_or_doc])

    # Status
    status = models.PositiveIntegerField(choices=WMO_STATUSES, default=NO_WMO)

    # References
    proposal = models.OneToOneField(Proposal, primary_key=True)

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a WMO"""
        self.update_status()
        super(Wmo, self).save(*args, **kwargs)

    def update_status(self):
        if self.metc == YES or (self.is_medical == YES and self.is_behavioristic == YES):
            if self.metc_decision and self.metc_decision_pdf:
                self.status = self.JUDGED
            else:
                self.status = self.WAITING
        else:
            self.status = self.NO_WMO

    def __unicode__(self):
        return _('WMO %s, status %s') % (self.proposal.title, self.status)
