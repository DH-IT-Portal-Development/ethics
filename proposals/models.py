from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

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
    TASKS_STARTED = 5
    TASKS_COMPLETED = 6
    INFORMED_CONSENT_UPLOADED = 7
    SUBMITTED = 8
    STATUSES = (
        (DRAFT, 'Algemene informatie ingevuld'),
        (WMO_AWAITING_DECISION, 'In afwachting beslissing WMO'),
        (WMO_COMPLETED, 'WMO-gedeelte afgerond'),
        (STUDY_CREATED, 'Kenmerken studie toegevoegd'),
        (TASKS_STARTED, 'Belasting proefpersoon aan het toevoegen'),
        (TASKS_COMPLETED, 'Belasting proefpersoon toegevoegd'),
        (INFORMED_CONSENT_UPLOADED, 'Informed consent geupload'),
        (SUBMITTED, 'Opgestuurd'),
    )

    # Fields of a proposal
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
en de beoogde methode voldoende helder is; verderop in deze aanmelding zal voor specifieke ingredi&#235;nten \
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
        'Is dit een studie waarbij dezelfde proefpersonen op meerdere dagen aan een sessie deelnemen? \
(bijvoorbeeld een longitudinale studie, of een kortlopende studie waar proefpersonen op twee of meer verschillende dagen getest worden)',
        default=False)

    # Fields with respect to tasks
    tasks_number = models.PositiveIntegerField(
        'Hoeveel taken worden er binnen deze studie bij de proefpersoon afgenomen?',
        null=True,
        help_text='Wanneer u bijvoorbeeld eerst de proefpersoon observeert en de proefpersoon vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. \
Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.')
    tasks_duration = models.PositiveIntegerField(
        'De totale geschatte netto taakduur van Uw sessie komt op basis van uw opgave per taak uit op <strong>{duration__sum} minuten</strong>. \
Hoe lang duurt de totale sessie, inclusief ontvangst, instructies per taak, pauzes tussen taken, en debriefing? (bij labbezoek dus van binnenkomst tot vertrek)',
        null=True)
    tasks_stressful = models.NullBooleanField(
        'Is het geheel van taken en overige activiteiten in de sessie als geheel belastend voor de proefpersoon op een manier die, \
ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega''s, bij de proefpersonen zelf, bij derden)? \
Denk hierbij bijvoorbeeld aan de totale duur, vermoeidheid, etc. \
Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de meest kwetsbare c.q. minst belastbare proefpersonengroep.')

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
        null=True)

    def gross_duration(self):
        return self.task_set.aggregate(models.Sum('duration'))

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
        if self.tasks_number: 
            status = self.TASKS_STARTED
        if self.task_set.count() == self.tasks_number:
            status = self.TASKS_COMPLETED
        if self.informed_consent_pdf: 
            status = self.INFORMED_CONSENT_UPLOADED
        return status

    def continue_url(self): 
        if self.status == self.DRAFT:
            return reverse('proposals:wmo_create', args=(self.id,))
        if self.status == self.WMO_AWAITING_DECISION:
            return reverse('proposals:wmo_update', args=(self.id,))
        if self.status == self.WMO_COMPLETED:
            return reverse('proposals:study_create', args=(self.id,))
        if self.status == self.STUDY_CREATED:
            return reverse('proposals:task_start', args=(self.id,))
        if self.status == self.TASKS_STARTED:
            return reverse('proposals:task_create', args=(self.id,))
        if self.status == self.TASKS_COMPLETED:
            return reverse('proposals:task_end', args=(self.id,))
        if self.status == self.INFORMED_CONSENT_UPLOADED:
            return reverse('proposals:submit', args=(self.id,))

    def __unicode__(self):
        return 'Proposal %s' % self.title

class Wmo(models.Model):
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

    # References
    proposal = models.OneToOneField(Proposal, primary_key=True)

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a Proposal"""
        self.proposal.save()
        super(Wmo, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Wmo %s' % self.proposal.title

class AgeGroup(models.Model):
    age_min = models.PositiveIntegerField()
    age_max = models.PositiveIntegerField(blank=True, null=True)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        if self.age_max: 
            return '%d-%d' % (self.age_min, self.age_max)
        else:
            return '%d+' % (self.age_min)

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
pati&#235;nten met afasie die een gesprek moeten voeren, ook al gaat het gesprek over alledaagse dingen). \
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
        default=True, 
        help_text='Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen proefpersonen te testen?')
    necessity_reason = models.TextField(
        'Leg uit waarom',
        blank=True)
    setting = models.ForeignKey(
        Setting,
        verbose_name='Geef aan waar de dataverzameling plaatsvindt')
    setting_details = models.CharField(
        'Namelijk', 
        max_length=200,
        blank=True)
    risk_physical = models.NullBooleanField(
        'Is de kans dat de proefpersoon fysiek letsel oploopt tijdens het afnemen van het experiment groter dan de kans op letsel in het dagelijks leven?',
        default=False)
    risk_psychological = models.NullBooleanField(
        'Is de kans dat de proefpersoon psychisch letsel oploopt tijdens het afnemen van het experiment groter dan de kans op letsel in het dagelijks leven?',
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
        self.proposal.save()
        super(Study, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Study details for proposal %s' % self.proposal.title

class Survey(models.Model):
    name = models.CharField(max_length=200)
    minutes = models.PositiveIntegerField()
    study = models.ForeignKey(Study)

    def __unicode__(self):
        return self.name

class Action(models.Model): 
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    info_text = models.TextField()

    def __unicode__(self):
        return self.description

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
        'Wat is de duur van deze taak van begin tot eind, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? \
Indien de taakduur per proefpersoon varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.')
    actions = models.ManyToManyField(
        Action,
        verbose_name='Wat vraag je bij deze taak de proefpersoon te doen?')
    actions_details = models.CharField(
        'Namelijk', 
        max_length=200, 
        blank=True)
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

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a Proposal"""
        self.proposal.save()
        super(Task, self).save(*args, **kwargs)

    # References
    proposal = models.ForeignKey(Proposal)

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
