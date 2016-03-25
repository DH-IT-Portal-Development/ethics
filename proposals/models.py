# -*- encoding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .validators import MaxWordsValidator


ALLOWED_CONTENT_TYPES = ['application/pdf', 'application/msword',
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
SUMMARY_MAX_WORDS = 200


def validate_pdf_or_doc(value):
    f = value.file
    if isinstance(f, UploadedFile) and f.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(_('Alleen .pdf- of .doc(x)-bestanden zijn toegestaan.'))


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
    WMO_DECISION_BY_ETCL = 2
    WMO_DECISION_BY_METC = 3
    STUDY_CREATED = 4
    STUDY_DESIGN = 5
    INTERVENTION_CREATED = 10
    OBSERVATION_CREATED = 20
    SESSIONS_STARTED = 30
    TASKS_STARTED = 31
    TASKS_ADDED = 32
    TASKS_ENDED = 33
    SESSIONS_ENDED = 34
    SUBMITTED_TO_SUPERVISOR = 40
    SUBMITTED = 50
    DECISION_MADE = 55
    WMO_DECISION_MADE = 60
    STATUSES = (
        (DRAFT, _('Algemene informatie ingevuld')),
        (WMO_DECISION_BY_ETCL, _('WMO: geen beoordeling door METC noodzakelijk')),
        (WMO_DECISION_BY_METC, _('WMO: wordt beoordeeld door METC')),
        (STUDY_CREATED, _('Kenmerken studie toegevoegd')),
        (STUDY_DESIGN, _('Opzet studie: gestart')),

        (INTERVENTION_CREATED, _('Nadere specificatie van het interventieonderdeel')),
        (OBSERVATION_CREATED, _('Nadere specificatie van het observatieonderdeel')),

        (SESSIONS_STARTED, _('Nadere specificatie van het takenonderdeel')),
        (TASKS_STARTED, _('Takenonderdeel: taken toevoegen')),
        (TASKS_ADDED, _('Takenonderdeel: alle taken toegevoegd')),
        (TASKS_ENDED, _('Takenonderdeel: afgerond')),

        (SESSIONS_ENDED, _('Opzet studie: afgerond')),

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
        _('Wat is de beoogde startdatum van uw studie?'))
    title = models.CharField(
        _('Wat is de titel van uw studie?'),
        max_length=200,
        unique=True,
        help_text=_('Kies s.v.p. een titel die niet volledig identiek is aan die van eerder ingediende studies.'))
    summary = models.TextField(
        _('Geef een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen. Gebruik maximaal 200 woorden.'),
        validators=[MaxWordsValidator(SUMMARY_MAX_WORDS)])
    other_applicants = models.BooleanField(
        _('Zijn er nog andere UiL OTS-onderzoekers bij deze studie betrokken?'),
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
        verbose_name=_('Wat is uw relatie tot het UiL OTS?'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_by')
    applicants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Uitvoerende(n)'),
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

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a Proposal"""
        self.status = self.get_status()
        super(Proposal, self).save(*args, **kwargs)

    def get_status(self):
        """Retrieves the current status for a Proposal"""
        status = self.status
        if hasattr(self, 'wmo'):
            wmo = self.wmo
            if wmo.status == wmo.WAITING:
                status = self.WMO_DECISION_BY_METC
            elif wmo.status == wmo.JUDGED:
                status = self.WMO_DECISION_MADE
            else:
                status = self.WMO_DECISION_BY_ETCL
        if hasattr(self, 'study'):
            status = self.STUDY_CREATED
            if self.study.has_observation:
                status = self.OBSERVATION_CREATED
            if self.study.has_intervention:
                status = self.INTERVENTION_CREATED
            if self.study.has_sessions:
                status = self.SESSIONS_STARTED

        session = self.current_session()
        if session:
            status = self.SESSIONS_STARTED
            if session.tasks_number:
                status = self.TASKS_STARTED
            if session.all_tasks_completed():
                status = self.TASKS_ADDED
            if session.tasks_duration:
                status = self.TASKS_ENDED
        if session and session.tasks_duration:
            if self.study.sessions_duration:
                status = self.SESSIONS_ENDED

        if self.date_submitted_supervisor:
            status = self.SUBMITTED_TO_SUPERVISOR
        if self.date_submitted:
            status = self.SUBMITTED
        if self.date_reviewed:
            status = self.DECISION_MADE

        return status

    def continue_url(self):
        session = self.current_session()
        if self.status == self.DRAFT:
            return reverse('proposals:wmo_create', args=(self.pk,))
        elif self.status == self.WMO_DECISION_BY_ETCL:
            return reverse('proposals:study_create', args=(self.pk,))
        elif self.status == self.WMO_DECISION_BY_METC:
            return reverse('proposals:wmo_update', args=(self.pk,))
        elif self.status == self.STUDY_CREATED:
            return reverse('proposals:study_design', args=(self.pk,))
        elif self.status == self.STUDY_DESIGN:
            return reverse('proposals:session_start', args=(self.pk,))
        elif self.status == self.SESSIONS_STARTED:
            return reverse('tasks:start', args=(session.pk,))
        elif self.status == self.TASKS_STARTED:
            return reverse('tasks:update', args=(session.current_task().pk,))
        elif self.status == self.TASKS_ADDED:
            return reverse('tasks:end', args=(session.pk,))
        elif self.status == self.TASKS_ENDED:
            return reverse('proposals:session_end', args=(self.pk,))
        elif self.status == self.SESSIONS_ENDED:
            return reverse('proposals:submit', args=(self.pk,))

        elif self.status == self.WMO_DECISION_MADE:
            return reverse('proposals:my_archive')

    def current_session(self):
        """
        Returns the current (incomplete) session.
        - If all sessions are completed, the last session is returned.
        - If no sessions have yet been created, None is returned.
        """
        current_session = None
        if hasattr(self, 'study'):
            for session in self.study.session_set.all():
                current_session = session
                if not session.tasks_duration:
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

    metc = models.NullBooleanField(
        _('Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?'))
    metc_institution = models.CharField(
        _('Welke instelling?'),
        max_length=200,
        blank=True)
    is_medical = models.NullBooleanField(
        _('Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?'),
        help_text=_('De definitie van medisch-wetenschappelijk onderzoek is: \
Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het beantwoorden van een vraag op het gebied van ziekte en gezondheid \
(etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, uitkomst of behandeling van ziekte), door het op systematische wijze vergaren en bestuderen van gegevens. \
Het onderzoek beoogt bij te dragen aan medische kennis die ook geldend is voor populaties buiten de directe onderzoekspopulatie. \
(CCMO-notitie, Definitie medisch-wetenschappelijk onderzoek, 2005, ccmo.nl)'))
    is_behavioristic = models.NullBooleanField(
        _('Worden de deelnemers aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?'),
        help_text=_('Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een deelnemer tot de deelnemer een knop/toets in laten drukken.'))
    metc_application = models.BooleanField(
        _('Uw studie moet beoordeeld worden door de METC, maar dient nog wel bij de ETCL te worden geregistreerd. Is voor deze studie al aangemeld bij een METC?'),
        default=False)
    metc_decision = models.BooleanField(
        _('Is de METC al tot een beslissing gekomen?'),
        default=False)
    metc_decision_pdf = models.FileField(
        _('Upload hier de beslissing van het METC (in .pdf of .doc(x)-formaat)'),
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
        self.proposal.save()

    def update_status(self):
        if self.metc or (self.is_medical and self.is_behavioristic):
            if self.metc_decision and self.metc_decision_pdf:
                self.status = self.JUDGED
            else:
                self.status = self.WAITING
        else:
            self.status = self.NO_WMO

    def __unicode__(self):
        return _('WMO %s, status %s') % (self.proposal.title, self.status)


class AgeGroup(models.Model):
    age_min = models.PositiveIntegerField()
    age_max = models.PositiveIntegerField(blank=True, null=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    max_net_duration = models.PositiveIntegerField()

    def __unicode__(self):
        if self.age_max:
            return _('%d-%d jaar') % (self.age_min, self.age_max)
        else:
            return _('%d+ jaar') % (self.age_min)


class Setting(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.description


class Compensation(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.description


class Recruitment(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.description


class Study(models.Model):
    OBSERVATION = 0
    INTERVENTION = 1
    SESSIONS = 2
    DESIGNS = (
        (OBSERVATION, _('Observatieonderzoek')),
        (INTERVENTION, _('Interventieonderzoek')),
        (SESSIONS, _('Taakonderzoek')),
    )

    age_groups = models.ManyToManyField(
        AgeGroup,
        verbose_name=_('Geef aan binnen welke leeftijdscategorie uw deelnemers vallen, \
er zijn meerdere antwoorden mogelijk'))
    legally_incapable = models.BooleanField(
        _('Maakt uw studie gebruik van <strong>volwassen</strong> wilsonbekwame deelnemers?'),
        default=False)
    has_traits = models.BooleanField(
        _(u'Deelnemers kunnen geïncludeerd worden op bepaalde bijzondere kenmerken. \
Is dit in uw studie bij (een deel van) de deelnemers het geval?'),
        default=False)
    necessity = models.NullBooleanField(
        _('Is het, om de onderzoeksvraag beantwoord te krijgen, noodzakelijk om het geselecteerde type \
deelnemer aan de studie te laten meedoen?'),
        help_text=_('Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen \
beantwoorden door volwassen deelnemers te testen?'))
    necessity_reason = models.TextField(
        _('Leg uit waarom'),
        blank=True)
    recruitment = models.ManyToManyField(
        Recruitment,
        verbose_name=_('Hoe worden de deelnemers geworven?'))
    recruitment_details = models.CharField(
        _('Licht toe'),
        max_length=200,
        blank=True)
    setting = models.ManyToManyField(
        Setting,
        verbose_name=_('Geef aan waar de dataverzameling plaatsvindt'))
    setting_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True)
    compensation = models.ForeignKey(
        Compensation,
        verbose_name=_('Welke vergoeding krijgt de deelnemer voor zijn/haar deelname aan deze studie?'),
        # TODO: put a proper text here.
        help_text=_('tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld'))
    compensation_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True)

    # Fields with respect to experimental design
    has_observation = models.BooleanField(
        _('Observatieonderzoek'),
        default=False)
    has_intervention = models.BooleanField(
        _('Interventieonderzoek'),
        default=False)
    has_sessions = models.BooleanField(
        _('Taakonderzoek'),
        default=False)

    # Fields with respect to informed consent
    informed_consent_pdf = models.FileField(
        _('Upload hier de toestemmingsverklaring (in .pdf of .doc(x)-formaat)'),
        blank=True,
        validators=[validate_pdf_or_doc])
    briefing_pdf = models.FileField(
        _('Upload hier de informatiebrief (in .pdf of .doc(x)-formaat)'),
        blank=True,
        validators=[validate_pdf_or_doc])
    passive_consent = models.BooleanField(
        _('Maakt uw studie gebruik van passieve informed consent?'),
        default=False,
        # TODO: link to website
        help_text=_('Wanneer u kinderen via een instelling (dus ook school) werft en u de ouders niet laat \
ondertekenen, maar in plaats daarvan de leiding van die instelling, dan maakt u gebruik van passieve informed consent. \
U kunt de templates vinden op <link website?>'))

    # Fields with respect to Sessions
    sessions_number = models.PositiveIntegerField(
        _('Hoeveel sessies telt deze studie?'),
        null=True,
        validators=[MinValueValidator(1)],
        help_text=_(u'Wanneer u bijvoorbeeld eerst de deelnemer een taak/aantal taken laat doen tijdens \
een eerste bezoek aan het lab en u laat de deelnemer nog een keer terugkomen om dezelfde taak/taken \
of andere taak/taken te doen, dan spreken we van twee sessies. \
Wanneer u meerdere taken afneemt op dezelfde dag, met pauzes daartussen, dan geldt dat toch als één sessie.'))
    sessions_duration = models.PositiveIntegerField(
        _('De netto duur van uw studie komt op basis van uw opgegeven tijd, uit op <strong>%d minuten</strong>. \
Wat is de totale duur van de gehele studie? Schat de totale tijd die de deelnemers kwijt zijn aan de studie.'),
        null=True,
        help_text=_('Dit is de geschatte totale bruto tijd die de deelnemer kwijt is aan alle sessies \
bij elkaar opgeteld, exclusief reistijd.'))
    stressful = models.NullBooleanField(
        _('Is de studie op onderdelen of als geheel zodanig belastend dat deze <em>ondanks de verkregen informed \
consent </em> vragen zou kunnen oproepen (of zelfs verontwaardiging), bijvoorbeeld bij collega-onderzoekers, \
bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers? Ga bij het beantwoorden van deze vraag uit \
van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep, en neem ook de leeftijd van de deelnemers \
in deze inschatting mee.'),
        help_text=mark_safe(_('Dit zou bijvoorbeeld het geval kunnen zijn bij een \'onmenselijk\' lange en uitputtende taak, \
een zeer confronterende vragenlijst, of voortdurend vernietigende feedback, maar ook bij een ervaren inbreuk op de \
privacy, of een ander ervaren gebrek aan respect. Let op, het gaat bij deze vraag om de door de deelnemer ervaren \
belasting tijdens het onderzoek, niet om de opgelopen psychische of fysieke schade door het onderzoek.')),
        default=False)
    stressful_details = models.TextField(
        _('Licht je antwoord toe. Geef concrete voorbeelden van de relevante aspecten van uw studie \
(bijv. representatieve voorbeelden van mogelijk zeer kwetsende woorden of uitspraken in de taak, \
of van zeer confronterende vragen in een vragenlijst), zodat de commissie zich een goed beeld kan vormen.'),
        blank=True)
    risk = models.NullBooleanField(
        _('Zijn de risico\'s op psychische, fysieke, of andere (bijv. economische, juridische) schade door deelname \
aan de studie <em>meer dan</em> minimaal? minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke schade bij de \
deelnemers duidelijk <em>boven</em> het "achtergrondrisico"? Achtergrondrisico is datgene dat gezonde, gemiddelde \
burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt. Ga bij het \
beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep in uw studie. \
En denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie \
kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, economische schade door data-koppeling, \
et cetera.'),
        help_text=mark_safe(_('Het achtergrondrisico voor psychische en fysieke schade omvat bijvoorbeeld ook de \
risico\'s van "routine"-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische \
contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-<em>assessment</em>, een \
intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles, waar relevant, \
onder begeleiding van adequaat geschoolde specialisten).')),
        default=False)
    risk_details = models.TextField(
        _('Licht toe'),
        max_length=200,
        blank=True)

    # Fields with respect to Surveys
    has_surveys = models.BooleanField(
        _(u'Worden er vragenlijsten afgenomen bij <em>een ander dan de deelnemer</em>? \
Denk hierbij aan de ouder of voogd van een kind, de leraar van de klas, de arts van een patiënt, etc.'),
        default=False)
    surveys_stressful = models.NullBooleanField(
        _('Is het invullen van deze vragenlijsten belastend? \
Denk hierbij bijv. aan het type vragen dat gesteld wordt en aan de tijd die de persoon kwijt is met het invullen van alle vragenlijsten.'),
        default=False)

    # References
    proposal = models.OneToOneField(Proposal, primary_key=True)

    def save(self, *args, **kwargs):
        """Sets the correct status on Proposal on save of a Study"""
        super(Study, self).save(*args, **kwargs)
        self.proposal.save()

    def net_duration(self):
        """Returns the duration of all Tasks in this Study"""
        sum = self.session_set.aggregate(models.Sum('tasks_duration'))['tasks_duration__sum']
        return sum or 0

    def first_session(self):
        """Returns the first Session in this Study"""
        return self.session_set.order_by('order')[0]

    def last_session(self):
        """Returns the last Session in this Study"""
        return self.session_set.order_by('-order')[0]

    def __unicode__(self):
        return _('Study details for proposal %s') % self.proposal.title


class Survey(models.Model):
    name = models.CharField(_('Naam vragenlijst'), max_length=200)
    minutes = models.PositiveIntegerField(_('Duur (in minuten)'))
    survey_url = models.URLField(_('URL'), blank=True)
    description = models.TextField(_('Korte beschrijving'))
    study = models.ForeignKey(Study)

    def __unicode__(self):
        return self.name
