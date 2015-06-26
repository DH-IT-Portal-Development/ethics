# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator


class Relation(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_supervisor = models.BooleanField(default=True)

    def __unicode__(self):
        return self.description


class Proposal(models.Model):
    DRAFT = 1
    WMO_AWAITING_DECISION = 2
    WMO_COMPLETED = 3
    STUDY_CREATED = 4
    SESSIONS_STARTED = 5
    TASKS_STARTED = 6
    TASKS_ADDED = 7
    TASKS_ENDED = 8
    SESSIONS_ENDED = 9
    INFORMED_CONSENT_UPLOADED = 10
    SUBMITTED = 11
    STATUSES = (
        (DRAFT, 'Algemene informatie ingevuld'),
        (WMO_AWAITING_DECISION, 'WMO: in afwachting beslissing'),
        (WMO_COMPLETED, 'WMO: afgerond'),
        (STUDY_CREATED, 'Kenmerken studie toegevoegd'),
        (SESSIONS_STARTED, 'Belasting proefpersoon: sessies toevoegen'),
        (TASKS_STARTED, 'Belasting proefpersoon: taken toevoegen'),
        (TASKS_ADDED, 'Belasting proefpersoon: alle taken toegevoegd'),
        (TASKS_ENDED, 'Belasting proefpersoon: afgerond'),
        (SESSIONS_ENDED, 'Belasting proefpersoon: afgerond'),
        (INFORMED_CONSENT_UPLOADED, 'Informed consent geupload'),
        (SUBMITTED, 'Opgestuurd'),
    )

    # Fields of a proposal
    reference_number = models.CharField(
        max_length=16,
        unique=True)
    title = models.CharField(
        'Wat is de titel van uw studie?',
        max_length=200,
        unique=True,
        help_text='Kies s.v.p. een titel die niet volledig identiek is aan die van eerder ingediende studies.')
    tech_summary = models.TextField(
        'Schrijf hier een samenvatting van 200-300 woorden, met daarin (a) een duidelijke, \
bondige beschrijving van de onderzoeksvraag of -vragen, en (b) een korte beschrijving van de beoogde methode, \
d.w.z. een mini-versie van de toekomstige Methode-sectie, met informatie over proefpersonen, materiaal (taken, stimuli), \
design, en procedure. Het gaat er hier vooral om dat de relatie tussen de onderzoeksvraag of -vragen \
en de beoogde methode voldoende helder is; verderop in deze aanmelding zal voor specifieke ingrediënten \
van de methode meer gedetailleerde informatie worden gevraagd.')
    supervisor_email = models.EmailField(
        'E-mailadres eindverantwoordelijke',
        blank=True,
        help_text='Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. \
Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.')
    other_applicants = models.BooleanField(
        'Zijn er nog andere UiL OTS-onderzoekers bij deze studie betrokken?',
        default=False)
    longitudinal = models.BooleanField(
        'Is dit een studie waarbij dezelfde proefpersonen op meerdere dagen deelnemen aan een sessie? \
(bijvoorbeeld een longitudinale studie, of een kortlopende studie waar proefpersonen op twee of meer verschillende dagen getest worden)',
        default=False)

    # Fields with respect to session
    sessions_number = models.PositiveIntegerField(
        'Hoeveel sessies telt deze studie?',
        null=True,
        help_text='Wanneer u bijvoorbeeld eerst de proefpersoon een taak/aantal taken laat doen tijdens \
een eerste bezoek aan het lab en u laat de proefpersoon nog een keer terugkomen om dezelfde taak/taken \
of andere taak/taken te doen, dan spreken we van twee sessies. \
Wanneer u meerdere taken afneemt op dezelfde dag, met pauzes daartussen, dan geldt dat toch als één sessie.')
    sessions_duration = models.PositiveIntegerField(
        'De totale geschatte netto studieduur van uw sessie komt op basis van uw opgave per sessie uit op <strong>%d minuten</strong>. \
Schat de totale tijd die uw proefpersonen aan de gehele studie zullen besteden.',
        null=True,
        help_text='Dit is de geschatte totale bruto tijd die de proefpersoon kwijt is aan alle sessie bij elkaar opgeteld, exclusief reistijd.')
    sessions_stressful = models.NullBooleanField(
        'Is het totaal van sessies als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, \
vragen zou kunnen oproepen (bijvoorbeeld bij collega''s, bij de proefpersonen zelf, bij derden)? \
Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, \
de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) \
of bepaald gedrag, etcetera. \
Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep.',
        default=False)
    sessions_stressful_details = models.CharField(
        'Waarom denkt u dat?',
        max_length=200,
        blank=True)

    # Fields with respect to informed consent
    informed_consent_pdf = models.FileField(
        'Upload hier de informed consent',
        blank=True)

    # Status
    status = models.PositiveIntegerField(choices=STATUSES, default=DRAFT)

    # Dates for bookkeeping
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_submitted = models.DateTimeField(null=True)

    # References to other models
    relation = models.ForeignKey(
        Relation,
        verbose_name='Wat is uw relatie tot het UiL OTS?')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_by')
    applicants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Uitvoerende(n)',
        related_name='applicants')
    parent = models.ForeignKey(
        'self',
        null=True,
        verbose_name='Te kopiëren aanvraag')

    def net_duration(self):
        return self.session_set.aggregate(models.Sum('tasks_duration'))['tasks_duration__sum']

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a Proposal"""
        self.status = self.get_status()
        super(Proposal, self).save(*args, **kwargs)

    def get_status(self):
        status = self.status
        if hasattr(self, 'wmo'):
            wmo = self.wmo
            if wmo.metc or (wmo.is_medical and wmo.is_behavioristic):
                if not wmo.metc_decision:
                    return self.WMO_AWAITING_DECISION
                if wmo.metc_decision and wmo.metc_decision_pdf:
                    status = self.WMO_COMPLETED
            else:
                status = self.WMO_COMPLETED
        if hasattr(self, 'study'):
            status = self.STUDY_CREATED
        if self.sessions_number:
            status = self.SESSIONS_STARTED

        session = self.current_session()
        if session:
            status = self.SESSIONS_STARTED
            if session.tasks_number:
                status = self.TASKS_STARTED
            if session.task_set.count() == session.tasks_number:
                status = self.TASKS_ADDED
            if session.tasks_duration:
                status = self.TASKS_ENDED

        if self.sessions_duration:
            status = self.SESSIONS_ENDED
        if self.informed_consent_pdf:
            status = self.INFORMED_CONSENT_UPLOADED
        return status

    def continue_url(self):
        session = self.current_session()
        if self.status == self.DRAFT:
            return reverse('proposals:wmo_create', args=(self.id,))
        if self.status == self.WMO_AWAITING_DECISION:
            return reverse('proposals:wmo_update', args=(self.id,))
        if self.status == self.WMO_COMPLETED:
            return reverse('proposals:study_create', args=(self.id,))
        if self.status == self.STUDY_CREATED:
            return reverse('proposals:session_start', args=(self.id,))
        if session:
            if self.status == self.SESSIONS_STARTED:
                return reverse('proposals:task_start', args=(session.id,))
            if self.status == self.TASKS_STARTED:
                return reverse('proposals:task_create', args=(session.id,))
            if self.status == self.TASKS_ADDED:
                return reverse('proposals:task_end', args=(session.id,))
        if self.status == self.TASKS_ENDED:
            return reverse('proposals:session_end', args=(self.id,))
        if self.status == self.SESSIONS_ENDED:
            return reverse('proposals:consent', args=(self.id,))
        if self.status == self.INFORMED_CONSENT_UPLOADED:
            return reverse('proposals:submit', args=(self.id,))

    def current_session(self):
        current_session = None
        for session in self.session_set.all():
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
        (NO_WMO, 'Geen beoordeling door METC noodzakelijk'),
        (WAITING, 'In afwachting beslissing METC'),
        (JUDGED, 'Beslissing METC geüpload'),
    )

    metc = models.NullBooleanField(
        'Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?')
    metc_institution = models.CharField(
        'Welke instelling?',
        max_length=200,
        blank=True)
    is_medical = models.NullBooleanField(
        'Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?',
        default=False)
    is_behavioristic = models.NullBooleanField(
        'Worden de proefpersonen aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?',
        help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een proefpersoon tot de proefpersoon een knop/toets in laten drukken.',
        default=False)
    metc_application = models.BooleanField(
        'Uw studie moet beoordeeld worden door de METC, maar dient nog wel bij de ETCL te worden geregistreerd. Is voor deze studie al een METC aanvraag ingediend?',
        default=False)
    metc_decision = models.BooleanField(
        'Is de METC al tot een beslissing gekomen?',
        default=False)
    metc_decision_pdf = models.FileField(
        'Upload hier de beslissing van het METC',
        blank=True)

    # Status
    status = models.PositiveIntegerField(choices=WMO_STATUSES, default=NO_WMO)

    # References
    proposal = models.OneToOneField(Proposal, primary_key=True)

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a WMO"""
        super(Wmo, self).save(*args, **kwargs)
        self.update_status()
        self.proposal.save()

    def update_status(self):
        if self.metc or (self.is_medical and self.is_behavioristic):
            if not self.metc_decision:
                self.status = self.WAITING
            if self.metc_decision and self.metc_decision_pdf:
                self.status = self.JUDGED
        else:
            self.status = self.NO_WMO

    def __unicode__(self):
        return 'WMO %s, status %s' % (self.proposal.title, self.status)


class AgeGroup(models.Model):
    age_min = models.PositiveIntegerField()
    age_max = models.PositiveIntegerField(blank=True, null=True)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        if self.age_max:
            return '%d-%d jaar' % (self.age_min, self.age_max)
        else:
            return '%d+ jaar' % (self.age_min)


class Trait(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description


class Setting(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description


class Compensation(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description


class Recruitment(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description


class Study(models.Model):
    age_groups = models.ManyToManyField(
        AgeGroup,
        verbose_name='Geef hieronder aan binnen welke leeftijdscategorie uw proefpersonen vallen, \
er zijn meerdere antwoorden mogelijk')
    has_traits = models.BooleanField(
        'Proefpersonen kunnen geselecteerd worden op bepaalde bijzondere kenmerken die mogelijk samenhangen met een verhoogde kwetsbaarheid of verminderde belastbaarheid t.a.v. aspecten van de beoogde studie \
(bijvoorbeeld: kinderen die vroeger gepest zijn in een onderzoek naar de neurale reactie op verbale beledigingen; \
patiënten met afasie die een gesprek moeten voeren, ook al gaat het gesprek over alledaagse dingen). \
Is dit in uw studie bij (een deel van) de proefpersonen het geval?',
        default=False)
    traits = models.ManyToManyField(
        Trait,
        blank=True,
        verbose_name='Selecteer de bijzondere kenmerken van uw proefpersonen')
    traits_details = models.CharField(
        'Namelijk',
        max_length=200,
        blank=True)
    necessity = models.NullBooleanField(
        'Is het om de onderzoeksvraag beantwoord te krijgen noodzakelijk om het geselecteerde type proefpersonen aan de studie te laten deelnemen?',
        help_text='Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen proefpersonen te testen?')
    necessity_reason = models.TextField(
        'Leg uit waarom',
        blank=True)
    setting = models.ManyToManyField(
        Setting,
        verbose_name='Geef aan waar de dataverzameling plaatsvindt')
    setting_details = models.CharField(
        'Namelijk',
        max_length=200,
        blank=True)
    risk_physical = models.NullBooleanField(
        'Is de kans dat de proefpersoon fysieke schade oploopt tijdens het afnemen van het experiment groter dan de kans op fysieke schade in het dagelijks leven?',
        default=False)
    risk_psychological = models.NullBooleanField(
        'Is de kans dat de proefpersoon psychische schade oploopt tijdens het afnemen van het experiment groter dan de kans op psychische schade in het dagelijks leven?',
        default=False)
    compensation = models.ForeignKey(
        Compensation,
        verbose_name='Welke vergoeding krijgt de proefpersoon voor zijn/haar deelname aan deze studie?',
        help_text='tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld')
    compensation_details = models.CharField(
        'Namelijk',
        max_length=200,
        blank=True)
    recruitment = models.ManyToManyField(
        Recruitment,
        verbose_name='Hoe worden de proefpersonen geworven?')
    recruitment_details = models.CharField(
        'Namelijk',
        max_length=200,
        blank=True)

    # References
    proposal = models.OneToOneField(Proposal, primary_key=True)

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a Proposal"""
        super(Study, self).save(*args, **kwargs)
        self.proposal.save()

    def __unicode__(self):
        return 'Study details for proposal %s' % self.proposal.title


class Session(models.Model):
    order = models.PositiveIntegerField()
    stressful = models.NullBooleanField(
        'Is het geheel van taken en overige activiteiten in de sessie als geheel belastend voor de proefpersoon op een manier die, \
ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega''s, bij de proefpersonen zelf, bij derden)? \
Denk hierbij bijvoorbeeld aan de totale duur, vermoeidheid, etc. \
Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de meest kwetsbare c.q. minst belastbare proefpersonengroep.')
    stressful_details = models.CharField(
        'Waarom denkt u dat?',
        max_length=200,
        blank=True)

    # Fields with respect to tasks
    tasks_number = models.PositiveIntegerField(
        'Hoeveel taken worden er binnen deze sessie bij de proefpersoon afgenomen?',
        null=True,
        help_text='Wanneer u bijvoorbeeld eerst de proefpersoon observeert en de proefpersoon vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. \
Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.')
    tasks_duration = models.PositiveIntegerField(
        'De totale geschatte netto taakduur van uw sessie komt op basis van uw opgave per taak uit op <strong>%d minuten</strong>. \
Hoe lang duurt <em>de totale sessie</em>, inclusief ontvangst, instructies per taak, pauzes tussen taken, en debriefing? (bij labbezoek dus van binnenkomst tot vertrek)',
        null=True)
    tasks_stressful = models.NullBooleanField(
        'Is het geheel van taken en overige activiteiten in de sessie als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, \
vragen zou kunnen oproepen (bijvoorbeeld bij collega''s, bij de proefpersonen zelf, bij derden)? \
Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, \
de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) \
of bepaald gedrag, etcetera. \
Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep.',
        default=False)
    tasks_stressful_details = models.CharField(
        'Waarom denkt u dat?',
        max_length=200,
        blank=True)

    # References
    proposal = models.ForeignKey(Proposal)

    class Meta:
        ordering = ['order']
        unique_together = ('proposal', 'order')

    def save(self, *args, **kwargs):
        """Sets the correct status on Proposal on save of a Session"""
        super(Session, self).save(*args, **kwargs)
        self.proposal.save()

    def net_duration(self):
        return self.task_set.aggregate(models.Sum('duration'))['duration__sum']

    def __unicode__(self):
        return 'Sessie {}'.format(self.order)


class Survey(models.Model):
    name = models.CharField(max_length=200)
    minutes = models.PositiveIntegerField()
    study = models.ForeignKey(Study)

    def __unicode__(self):
        return self.name


class Registration(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description


class Task(models.Model):
    name = models.CharField(
        'Wat is de naam of korte beschrijving van de taak? (geef alleen een naam als daarmee volledig duidelijk is waar het om gaat, bijv "lexicale decisietaak")',
        max_length=200)
    duration = models.PositiveIntegerField(
        'Wat is de duur van deze taak van begin tot eind in minuten, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? \
Indien de taakduur per proefpersoon varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.',
        default=0,
        validators=[MinValueValidator(1)])
    registrations = models.ManyToManyField(
        Registration,
        verbose_name='Hoe wordt het gedrag of de toestand van de proefpersoon bij deze taak vastgelegd?')
    registrations_details = models.CharField(
        'Namelijk',
        max_length=200,
        blank=True)
    feedback = models.BooleanField(
        'Krijgt de proefpersoon tijdens of na deze taak feedback op zijn/haar gedrag of toestand?',
        default=False)
    feedback_details = models.CharField(
        'Van welke aard is deze feedback?',
        max_length=200,
        blank=True)
    stressful = models.NullBooleanField(
        'Is deze taak belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, \
vragen zou kunnen oproepen (bijvoorbeeld bij collega''s, bij de proefpersonen zelf, bij derden)? \
Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, \
de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) \
of bepaald gedrag, etcetera. \
En ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep.',
        default=False)
    stressful_details = models.CharField(
        'Waarom denkt u dat?',
        max_length=200,
        blank=True)

    # References
    session = models.ForeignKey(Session)

    def save(self, *args, **kwargs):
        """Sets the correct status on Proposal on save of a Task"""
        super(Task, self).save(*args, **kwargs)
        self.session.proposal.save()

    def delete(self, *args, **kwargs):
        """Removes the totals on Session level on deletion of a Task"""
        session = self.session
        session.tasks_duration = None
        session.tasks_stressful = None
        session.tasks_stressful_details = ''
        super(Task, self).delete(*args, **kwargs)
        session.save()


class Faq(models.Model):
    order = models.PositiveIntegerField(unique=True)
    question = models.TextField()
    answer = models.TextField()

    class Meta:
        verbose_name = 'FAQ'

    def __unicode__(self):
        return self.question


class Member(models.Model):
    title = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Meeting(models.Model):
    date = models.DateField()
    deadline = models.DateField()

    def __unicode__(self):
        return '%s' % (self.date)
